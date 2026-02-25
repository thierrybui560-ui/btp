# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.

import base64
import csv
import io
import re
import unicodedata
from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError


def _normalize_header(name):
    """Normalize CSV header for matching: strip BOM, accents, spaces, lower, spaces/dashes to underscores."""
    if not name:
        return ''
    s = (name.replace('\ufeff', '') or '').strip().lower()
    # Normalize accents (e.g. Débit -> debit, Montant -> montant)
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    s = re.sub(r'[\s\-]+', '_', s)
    return s


# Accepted column names (normalized): date, amount (signed), debit/credit (pair), label
DATE_ALIASES = frozenset((
    'date', 'transaction_date', 'value_date', 'booking_date',
    'transactiondate', 'valuedate', 'bookingdate', 'operation_date',
))
# Single column meaning signed amount (positive=in, negative=out)
AMOUNT_ALIASES = frozenset((
    'amount', 'montant', 'sum', 'total', 'balance', 'balance_change',
    'transaction_amount', 'amount_eur', 'montant_eur',
))
# Substrings that identify an amount-like column when exact match fails
AMOUNT_SUBSTRINGS = ('amount', 'montant', 'sum', 'total', 'balance')
LABEL_ALIASES = frozenset((
    'label', 'payment_ref', 'reference', 'libelle', 'name', 'description',
    'details', 'memo', 'remark', 'remarks', 'narration', 'concept',
))


class BtpBankStatementImportWizard(models.TransientModel):
    _name = 'btp.bank.statement.import.wizard'
    _description = 'Import Bank Statement (CSV)'

    journal_id = fields.Many2one(
        'account.journal',
        string='Bank Journal',
        required=True,
        domain=[('type', '=', 'bank')],
        help='Journal to import the statement into.',
    )
    data_file = fields.Binary(
        string='CSV File',
        required=True,
        attachment=False,
    )
    filename = fields.Char(string='Filename')
    date_format = fields.Char(
        string='Date format',
        default='%Y-%m-%d',
        help='e.g. %%Y-%%m-%%d for 2025-01-15, %%d/%%m/%%Y for 15/01/2025',
    )

    def _detect_delimiter(self, content):
        """Detect CSV delimiter from first line (comma vs semicolon)."""
        first_line = (content.split('\n') or [''])[0]
        if ';' in first_line and ',' not in first_line:
            return ';'
        if ';' in first_line and first_line.count(';') >= first_line.count(','):
            return ';'
        return ','

    def _parse_csv(self):
        """Parse CSV; yield dicts with keys: date, amount, label (payment_ref)."""
        self.ensure_one()
        if not self.data_file:
            raise UserError(_('Please upload a CSV file.'))
        raw = self.data_file
        # Binary field can be: base64 str, file bytes, or bytes containing base64 ASCII
        if isinstance(raw, str):
            raw = base64.b64decode(raw)
        elif isinstance(raw, bytes):
            # Odoo may store the base64-encoded string as bytes; decode and b64decode to get file content
            try:
                as_str = raw.decode('ascii', errors='strict').strip()
                if len(as_str) > 50 and all(
                    c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r\t '
                    for c in as_str
                ):
                    decoded = base64.b64decode(as_str)
                    sample = decoded[:200].decode('utf-8', errors='replace').lower()
                    if 'date' in sample or 'debit' in sample or 'amount' in sample or 'montant' in sample:
                        raw = decoded
            except (ValueError, UnicodeDecodeError, Exception):
                pass
        content = raw.decode('utf-8-sig', errors='replace').strip()
        delimiter = self._detect_delimiter(content)
        try:
            reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
            rows_list = list(reader)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        except Exception as e:
            raise UserError(_('Invalid CSV: %s') % e)
        if not fieldnames:
            raise UserError(_('CSV has no header row.'))

        # Normalize column names (BOM, strip, lower, spaces/dashes -> underscores)
        normalized = [_normalize_header(f) for f in fieldnames]
        # Map normalized -> original index to get key in row dict (use original fieldnames for row keys)
        name_to_original = dict(zip(normalized, fieldnames))

        def get_norm(name):
            return _normalize_header(name)

        date_col = next((name_to_original[f] for f in normalized if f in DATE_ALIASES), None)
        if not date_col:
            date_col = next((name_to_original[f] for f in normalized if 'date' in f), None)

        has_debit_credit = 'debit' in normalized and 'credit' in normalized
        amount_col = None
        if not has_debit_credit:
            amount_col = next((name_to_original[f] for f in normalized if f in AMOUNT_ALIASES), None)
            if not amount_col:
                amount_col = next(
                    (name_to_original[f] for f in normalized if any(s in f for s in AMOUNT_SUBSTRINGS)),
                    None,
                )
        if not amount_col and not has_debit_credit:
            seen = ', '.join('"%s"' % f for f in fieldnames[:15])
            if len(fieldnames) > 15:
                seen += ', ...'
            raise UserError(
                _('CSV must have a column for amount. Use one of: "amount", "montant", "debit"+ "credit", or a column whose name contains "amount"/"montant". Detected columns: %s')
                % seen
            )
        label_col = next(
            (name_to_original[f] for f in normalized if f in LABEL_ALIASES),
            name_to_original.get(normalized[0]) if normalized else None,
        )
        debit_col = name_to_original.get('debit')
        credit_col = name_to_original.get('credit')

        def _num(s):
            s = (s or '0').strip().replace(',', '.').replace(' ', '')
            return float(s) if s else 0.0

        fmt = (self.date_format or '%Y-%m-%d').replace('%%', '%')
        for row in rows_list:
            # Amount: single signed column or debit/credit pair
            if has_debit_credit and debit_col is not None and credit_col is not None:
                try:
                    d = _num(row.get(debit_col))
                    c = _num(row.get(credit_col))
                    amount = c - d  # credit - debit for bank (inflow positive)
                except (ValueError, TypeError):
                    continue
            elif amount_col:
                try:
                    amount = _num(row.get(amount_col))
                except (ValueError, TypeError):
                    continue
            else:
                continue
            if amount == 0:
                continue
            # Date
            raw_date = (date_col and (row.get(date_col) or '').strip()) or ''
            if not raw_date:
                continue
            try:
                dt = datetime.strptime(raw_date, fmt)
                date = dt.date()
            except ValueError:
                for f in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d.%m.%Y'):
                    try:
                        dt = datetime.strptime(raw_date, f)
                        date = dt.date()
                        break
                    except ValueError:
                        continue
                else:
                    continue
            # Label
            label = (label_col and (row.get(label_col) or '').strip()) or str(amount)
            if isinstance(label, bytes):
                label = label.decode('utf-8', errors='replace')
            yield {'date': date, 'amount': amount, 'payment_ref': (label or '')[:200] if label else ''}

    def action_import(self):
        self.ensure_one()
        if self.journal_id.type != 'bank':
            raise UserError(_('Select a Bank journal.'))
        company = self.journal_id.company_id
        rows = list(self._parse_csv())
        if not rows:
            raise UserError(_('No valid rows found in the CSV. Use columns: date, amount, and optionally label (or payment_ref, reference).'))
        # Create statement
        st_vals = {
            'journal_id': self.journal_id.id,
            'date': min(r['date'] for r in rows),
            'balance_start': 0.0,
            'reference': self.filename or 'CSV Import',
        }
        # Create as sudo so users with Invoicing/Readonly can import (Odoo restricts create to group_account_basic)
        statement = self.env['account.bank.statement'].sudo().create(st_vals)
        # Create lines (order by date then by row order)
        indexed = list(enumerate(rows))
        line_vals = []
        for seq, (_ignored, row) in enumerate(sorted(indexed, key=lambda x: (x[1]['date'], x[0])), start=1):
            line_vals.append({
                'statement_id': statement.id,
                'journal_id': self.journal_id.id,
                'date': row['date'],
                'amount': row['amount'],
                'payment_ref': row['payment_ref'],
                'sequence': seq,
            })
        self.env['account.bank.statement.line'].sudo().create(line_vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.bank.statement',
            'res_id': statement.id,
            'view_mode': 'form',
            'target': 'current',
        }
