# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class BtpSituation(models.Model):
    _name = 'btp.situation'
    _description = 'BTP Monthly Situation (Progress)'
    _order = 'site_id desc, situation_date desc, id desc'

    name = fields.Char(
        string='Reference',
        compute='_compute_name',
        store=True,
        readonly=True,
    )
    site_id = fields.Many2one(
        'project.project',
        string='Site',
        required=True,
        ondelete='cascade',
        index=True,
    )
    situation_date = fields.Date(
        string='Situation Date',
        required=True,
        help='End of month for this situation (e.g. last day of January)',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('invoiced', 'Invoiced'),
    ], string='Status', default='draft', required=True, copy=False, tracking=True)
    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        copy=False,
        readonly=True,
        help='Customer invoice created from this situation',
    )
    line_ids = fields.One2many(
        'btp.situation.line',
        'situation_id',
        string='Lines',
        copy=True,
    )
    amount_total = fields.Float(
        string='Total Progress',
        digits='Product Price',
        compute='_compute_amount_total',
        store=True,
    )
    amount_retention = fields.Float(
        string='Retention',
        digits='Product Price',
        compute='_compute_amount_retention',
        store=True,
    )
    amount_to_invoice = fields.Float(
        string='Amount to Invoice',
        digits='Product Price',
        compute='_compute_amount_to_invoice',
        store=True,
    )

    @api.depends('site_id', 'situation_date')
    def _compute_name(self):
        for s in self:
            if s.site_id and s.situation_date:
                s.name = _('%s – Situation %s') % (
                    s.site_id.name or s.site_id.btp_site_code or 'Site',
                    s.situation_date.strftime('%Y-%m'),
                )
            else:
                s.name = _('New Situation')

    @api.depends('line_ids', 'line_ids.month_progress')
    def _compute_amount_total(self):
        for s in self:
            s.amount_total = sum(s.line_ids.mapped('month_progress'))

    @api.depends('amount_total', 'site_id', 'site_id.btp_retention_rate')
    def _compute_amount_retention(self):
        for s in self:
            rate = (s.site_id.btp_retention_rate or 0.0) / 100.0
            s.amount_retention = s.amount_total * rate

    @api.depends('amount_total', 'amount_retention')
    def _compute_amount_to_invoice(self):
        for s in self:
            s.amount_to_invoice = s.amount_total - s.amount_retention

    @api.constrains('situation_date', 'site_id')
    def _check_situation_date_unique(self):
        for s in self:
            if not s.site_id or not s.situation_date:
                continue
            same = self.search([
                ('site_id', '=', s.site_id.id),
                ('situation_date', '=', s.situation_date),
                ('id', '!=', s.id),
            ], limit=1)
            if same:
                raise ValidationError(
                    _('A situation for %s already exists for %s.')
                    % (s.site_id.name, s.situation_date.strftime('%Y-%m'))
                )

    def action_confirm(self):
        for s in self:
            if s.state != 'draft':
                raise UserError(_('Only draft situations can be confirmed.'))
            if not s.line_ids:
                raise UserError(_('Add at least one line before confirming.'))
        self.write({'state': 'confirmed'})
        return True

    def action_create_invoice(self):
        """Create a customer invoice from this situation (BTP type = situation)."""
        self.ensure_one()
        if self.state == 'invoiced' and self.invoice_id:
            return self.action_view_invoice()
        if self.state != 'confirmed':
            raise UserError(_('Confirm the situation before creating the invoice.'))
        site = self.site_id
        site._btp_assert_not_blocked()
        if not site.partner_id:
            raise UserError(_('Site must have a client (Partner) set.'))
        order = site.btp_sale_order_id
        if not order:
            raise UserError(_('Site must have a linked Sale Order for invoicing.'))

        company = site.company_id or self.env.company
        journal = self.env['account.journal'].search([
            ('company_id', '=', company.id),
            ('type', '=', 'sale'),
        ], limit=1)
        if not journal:
            raise UserError(_('No sales journal found for the company. Create a journal of type "Sales" in Accounting → Configuration → Journals for company "%s".') % (company.name or _('current')))

        seq_date = self.situation_date or fields.Date.today()
        btp_sequence = self.env['ir.sequence'].next_by_code(
            'btp.invoice', sequence_date=seq_date
        )
        if not btp_sequence:
            raise UserError(_('BTP invoice sequence is not configured.'))

        product = self.env.ref(
            'btp_prospecting.product_btp_quote_item_service_template',
            raise_if_not_found=False,
        )
        product_id = product.product_variant_id if product else False
        account = False
        if product_id and product_id.property_account_income_id:
            account = product_id.property_account_income_id
        if not account:
            account = self.env['account.account'].search([
                ('company_ids', 'in', [company.id]),
                ('account_type', 'in', ('income', 'income_other')),
            ], limit=1)
        if not account:
            raise UserError(_(
                'No income account found for invoice lines. For company "%s", either: '
                '(1) Set an Income account on the BTP service product (Inventory or Invoicing → Products → [BTP product] → Accounting tab), '
                'or (2) Set a default Income account on the product category, '
                'or (3) Ensure your Chart of Accounts has at least one account of type Income (Accounting → Configuration → Chart of Accounts).'
            ) % (company.name or _('current')))

        line_vals = []
        for line in self.line_ids:
            if line.month_progress <= 0:
                continue
            line_vals.append((0, 0, {
                'name': line.quote_item_id.name if line.quote_item_id else line.name or _('Progress'),
                'quantity': 1.0,
                'price_unit': line.month_progress,
                'account_id': account.id,
                'product_id': product_id.id if product_id else False,
            }))
        if not line_vals:
            raise UserError(_('No positive progress to invoice.'))

        retention_rate = site.btp_retention_rate or 0.0
        retention_amount = self.amount_retention
        amount_to_invoice = self.amount_to_invoice  # total - retention

        # Deposit deduction: deduct from deposit up to amount_to_invoice
        Move = self.env['account.move']
        remaining_deposit = Move._btp_remaining_deposit_for_site(site)
        deposit_deduction = min(amount_to_invoice, remaining_deposit) if remaining_deposit > 0 else 0.0
        if deposit_deduction > 0:
            line_vals.append((0, 0, {
                'name': _('Deduction of deposit'),
                'quantity': 1.0,
                'price_unit': -deposit_deduction,
                'account_id': account.id,
                'product_id': product_id.id if product_id else False,
            }))

        move_vals = {
            'move_type': 'out_invoice',
            'partner_id': site.partner_id.id,
            'invoice_date': self.situation_date,
            'ref': self.name,
            'btp_invoice_type': 'situation',
            'btp_invoice_sequence': btp_sequence,
            'btp_site_id': site.id,
            'btp_situation_id': self.id,
            'btp_retention_rate': retention_rate,
            'btp_retention_amount': retention_amount,
            'btp_deposit_deduction': deposit_deduction,
            'journal_id': journal.id,
            'invoice_line_ids': line_vals,
        }
        move = self.env['account.move'].create(move_vals)
        self.write({'state': 'invoiced', 'invoice_id': move.id})
        return self.action_view_invoice()

    def action_view_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            return True
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
            'context': {'default_move_type': 'out_invoice'},
        }

    def action_set_draft(self):
        self.filtered(lambda s: s.state == 'confirmed' and not s.invoice_id).write({'state': 'draft'})
        return True
