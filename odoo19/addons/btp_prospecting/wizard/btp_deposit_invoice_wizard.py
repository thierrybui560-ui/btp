# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BtpDepositInvoiceWizard(models.TransientModel):
    _name = 'btp.deposit.invoice.wizard'
    _description = 'Create BTP Deposit Invoice'

    site_id = fields.Many2one(
        'project.project',
        string='Site',
        required=True,
        ondelete='cascade',
    )
    amount = fields.Float(
        string='Deposit Amount',
        digits='Product Price',
        required=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='site_id.company_id.currency_id',
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_model') == 'project.project' and self.env.context.get('active_id'):
            site = self.env['project.project'].browse(self.env.context['active_id'])
            res['site_id'] = site.id
            if site.btp_sale_order_id and site.btp_sale_order_id.amount_total:
                res['amount'] = site.btp_sale_order_id.amount_total * 0.10
            else:
                res['amount'] = 0.0
        return res

    def action_create_deposit_invoice(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_('Deposit amount must be positive.'))
        site = self.site_id
        if not site.partner_id:
            raise UserError(_('Site must have a client (Partner) set.'))
        company = site.company_id or self.env.company
        journal = self.env['account.journal'].search([
            ('company_id', '=', company.id),
            ('type', '=', 'sale'),
        ], limit=1)
        if not journal:
            raise UserError(_('No sales journal found for the company. Create a journal of type "Sales" in Accounting → Configuration → Journals for company "%s".') % (company.name or _('current')))
        btp_sequence = self.env['ir.sequence'].next_by_code(
            'btp.invoice',
            sequence_date=fields.Date.today(),
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
                'No income account found for invoice lines. For company "%s", set an Income account on the BTP service product (Accounting tab) or ensure the Chart of Accounts has an account of type Income.'
            ) % (company.name or _('current')))

        line_vals = [(0, 0, {
            'name': _('Deposit - %s') % (site.name or site.btp_site_code or 'Site'),
            'quantity': 1.0,
            'price_unit': self.amount,
            'account_id': account.id,
            'product_id': product_id.id if product_id else False,
        })]

        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': site.partner_id.id,
            'invoice_date': fields.Date.today(),
            'ref': _('Deposit - %s') % (site.name or site.btp_site_code or ''),
            'btp_invoice_type': 'deposit',
            'btp_invoice_sequence': btp_sequence,
            'btp_site_id': site.id,
            'journal_id': journal.id,
            'invoice_line_ids': line_vals,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
            'context': {'default_move_type': 'out_invoice'},
        }
