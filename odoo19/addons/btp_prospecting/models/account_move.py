# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    btp_invoice_type = fields.Selection([
        ('standard', 'Standard'),
        ('situation', 'Monthly Situation'),
        ('deposit', 'Deposit'),
        ('final', 'Final Invoice'),
    ], string='BTP Invoice Type', default='standard', copy=False, tracking=True,
       help='Type of BTP invoice: situation (progress), deposit, or final.')
    btp_invoice_sequence = fields.Char(
        string='BTP Number',
        copy=False,
        readonly=True,
        index=True,
        help='Invoice number in format YYYYMMNNN (e.g. 202501001)',
    )
    _BTP_REVISION_LETTERS = [('', '')] + [(c, c) for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']

    btp_revision_index = fields.Selection(
        _BTP_REVISION_LETTERS,
        string='Revision',
        copy=False,
        help='Revision letter (A, B, C…) for modified/re-issued invoices. Set automatically when you use "Create revision" (editable in draft only).',
    )
    btp_site_id = fields.Many2one(
        'project.project',
        string='Site',
        copy=False,
        ondelete='set null',
        index=True,
    )
    btp_situation_id = fields.Many2one(
        'btp.situation',
        string='Situation',
        copy=False,
        ondelete='set null',
        readonly=True,
    )
    btp_retention_rate = fields.Float(
        string='Retention Rate %',
        digits=(5, 2),
        copy=False,
        help='Retention of guarantee rate (e.g. 5%)',
    )
    btp_retention_amount = fields.Float(
        string='Retention Amount',
        digits='Product Price',
        copy=False,
        help='Retained amount (guarantee)',
    )
    btp_reminder_status = fields.Selection([
        ('0', 'None'),
        ('1', '1st reminder'),
        ('2', '2nd reminder'),
        ('formal', 'Formal notice'),
    ], string='Reminder Status', default='0', copy=False, tracking=True)
    btp_reminder_courtesy_sent = fields.Datetime(
        string='Courtesy Reminder Sent',
        copy=False,
        readonly=True,
        help='D-7 reminder sent',
    )
    btp_reminder_official_sent = fields.Datetime(
        string='Official Reminder Sent',
        copy=False,
        readonly=True,
        help='D0 reminder sent',
    )
    btp_deposit_deduction = fields.Float(
        string='Deposit Deduction',
        digits='Product Price',
        copy=False,
        default=0.0,
        help='Amount deducted from deposit on this situation invoice (stored for tracking).',
    )

    @api.model
    def default_get(self, fields_list):
        """Ensure New from Client/Supplier Outstanding opens the correct form and has a due date
        so Confirm does not raise 'Any journal item on a payable account must have a due date'."""
        res = super().default_get(fields_list)
        move_type = res.get('move_type') or self.env.context.get('default_move_type')
        if move_type in ('in_invoice', 'in_refund', 'out_invoice', 'out_refund', 'out_receipt', 'in_receipt'):
            if not res.get('move_type'):
                res['move_type'] = move_type
            # Always default due date for invoices/bills so payable/receivable lines get date_maturity (form may not request invoice_date_due in fields_list)
            if move_type in ('in_invoice', 'out_invoice', 'in_refund', 'out_refund') and not res.get('invoice_date_due'):
                res['invoice_date_due'] = fields.Date.context_today(self)
        return res

    def _btp_get_next_revision_letter(self):
        """Return the next revision letter (A, B, C…) for the same BTP number.
        Used when creating a revision so the user never picks the same letter.
        """
        self.ensure_one()
        if not self.btp_invoice_sequence:
            return 'A'
        same_number = self.search([
            ('btp_invoice_sequence', '=', self.btp_invoice_sequence),
            ('company_id', '=', self.company_id.id),
        ])
        letters = [m.btp_revision_index for m in same_number if m.btp_revision_index]
        if not letters:
            return 'A'
        max_letter = max(letters)
        if max_letter == 'Z':
            raise UserError(_('Maximum number of revisions (A–Z) reached for BTP number %s.') % self.btp_invoice_sequence)
        return chr(ord(max_letter) + 1)

    def action_btp_create_revision(self):
        """Create a new draft invoice as a revision of this one: same BTP number, next revision letter (A, B, C…)."""
        self.ensure_one()
        if self.move_type != 'out_invoice':
            raise UserError(_('Only customer invoices can be revised.'))
        if self.state != 'posted':
            raise UserError(_('Only posted invoices can be used to create a revision. Post this invoice first.'))
        if not self.btp_invoice_sequence:
            raise UserError(_('This invoice has no BTP number; revisions require a BTP number.'))
        next_letter = self._btp_get_next_revision_letter()
        new_move = self.copy(default={
            'btp_invoice_sequence': self.btp_invoice_sequence,
            'btp_revision_index': next_letter,
            'btp_reminder_status': '0',
            'btp_reminder_courtesy_sent': False,
            'btp_reminder_official_sent': False,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': new_move.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.depends('payment_state', 'invoice_date_due', 'move_type')
    def _compute_btp_invoice_status(self):
        """Helper: paid / pending / late for display. Empty for non-customer invoices."""
        today = fields.Date.context_today(self)
        for move in self:
            if move.move_type not in ('out_invoice', 'out_refund'):
                move.btp_invoice_status_display = False
                continue
            if move.payment_state == 'paid':
                move.btp_invoice_status_display = 'paid'
            elif move.invoice_date_due and move.invoice_date_due < today:
                move.btp_invoice_status_display = 'late'
            else:
                move.btp_invoice_status_display = 'pending'

    btp_invoice_status_display = fields.Char(
        string='Status',
        compute='_compute_btp_invoice_status',
        help='paid / pending / late for BTP follow-up',
    )
    btp_due_bucket = fields.Selection(
        [
            ('paid', 'Paid'),
            ('in_payment', 'In Payment'),
            ('overdue', 'Overdue'),
            ('due_soon', 'Due <= 7 days'),
            ('pending', 'Pending'),
        ],
        string='Due Bucket',
        compute='_compute_btp_due_bucket',
        store=True,
        help='Normalized due status used by list decorations and KPI reporting.',
    )

    @api.depends('payment_state', 'invoice_date_due', 'move_type')
    def _compute_btp_due_bucket(self):
        today = fields.Date.context_today(self)
        for move in self:
            if move.move_type not in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund'):
                move.btp_due_bucket = False
                continue
            if move.payment_state == 'paid':
                move.btp_due_bucket = 'paid'
                continue
            if move.payment_state == 'in_payment':
                move.btp_due_bucket = 'in_payment'
                continue
            due = move.invoice_date_due
            if not due:
                move.btp_due_bucket = 'pending'
                continue
            if due < today:
                move.btp_due_bucket = 'overdue'
            elif (due - today).days <= 7:
                move.btp_due_bucket = 'due_soon'
            else:
                move.btp_due_bucket = 'pending'

    def _get_valid_journal_types(self):
        """When opening New from Supplier Outstanding, context has default_move_type='in_invoice'
        but the record may not have move_type set yet; request purchase journal instead of general."""
        move_type = self.move_type or self.env.context.get('default_move_type')
        if move_type in ('in_invoice', 'in_refund'):
            return ['purchase']
        return super()._get_valid_journal_types()

    def _btp_remaining_deposit_for_site(self, site):
        """Total posted deposit amount for site minus already deducted on situation invoices."""
        if not site:
            return 0.0
        deposit_total = sum(
            self.search([
                ('btp_site_id', '=', site.id),
                ('btp_invoice_type', '=', 'deposit'),
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice'),
            ]).mapped('amount_total')
        ) or 0.0
        deducted = sum(
            self.search([
                ('btp_site_id', '=', site.id),
                ('btp_invoice_type', '=', 'situation'),
                ('state', 'in', ('posted', 'draft')),
            ]).mapped('btp_deposit_deduction')
        ) or 0.0
        return max(0.0, deposit_total - deducted)

    @api.model
    def _cron_btp_invoice_reminders(self):
        """Update reminder status and send reminder emails (D-7, D0, D+15, D+30 formal)."""
        today = fields.Date.context_today(self)
        domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '!=', 'paid'),
            ('invoice_date_due', '!=', False),
            ('btp_site_id', '!=', False),
        ]
        for move in self.search(domain):
            due = move.invoice_date_due
            days_until_due = (due - today).days if due else 0
            days_late = (today - due).days if due and today >= due else 0

            # D-7: courtesy reminder (before due)
            if days_until_due <= 7 and days_until_due >= 0 and not move.btp_reminder_courtesy_sent:
                move._btp_send_reminder_email('courtesy')

            # D0: official reminder (on or after due)
            if today >= due and not move.btp_reminder_official_sent:
                move._btp_send_reminder_email('official')

            # After due: 1st (D+15), 2nd (D+30), formal (D+30 when 2nd already sent)
            if today < due:
                continue
            if days_late >= 30 and move.btp_reminder_status == '2':
                if move._btp_send_reminder_email('formal'):
                    move.write({'btp_reminder_status': 'formal'})
            elif days_late >= 30 and move.btp_reminder_status == '1':
                if move._btp_send_reminder_email('2nd'):
                    move.write({'btp_reminder_status': '2'})
            elif days_late >= 15 and move.btp_reminder_status == '0':
                if move._btp_send_reminder_email('1st'):
                    move.write({'btp_reminder_status': '1'})

    def _btp_send_reminder_email(self, reminder_kind):
        """Send reminder email using mail template. Sets sent flags only when send succeeds."""
        self.ensure_one()
        template_xmlids = {
            'courtesy': 'btp_prospecting.email_template_btp_invoice_reminder_courtesy',
            'official': 'btp_prospecting.email_template_btp_invoice_reminder_official',
            '1st': 'btp_prospecting.email_template_btp_invoice_reminder_1st',
            '2nd': 'btp_prospecting.email_template_btp_invoice_reminder_2nd',
            'formal': 'btp_prospecting.email_template_btp_invoice_reminder_formal',
        }
        template = self.env.ref(template_xmlids.get(reminder_kind), raise_if_not_found=False)
        sent = False
        if template:
            try:
                template.send_mail(self.id, force_send=True)
                sent = True
            except Exception:
                sent = False
        if not sent:
            return False
        now = fields.Datetime.now()
        if reminder_kind == 'courtesy':
            self.write({'btp_reminder_courtesy_sent': now})
        elif reminder_kind == 'official':
            self.write({'btp_reminder_official_sent': now})
        return True
