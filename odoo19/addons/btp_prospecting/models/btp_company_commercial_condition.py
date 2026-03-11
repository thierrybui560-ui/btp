# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BtpCompanyCommercialCondition(models.Model):
    _name = 'btp.company.commercial.condition'
    _description = 'BTP Company Commercial Condition'
    _order = 'company_id, id desc'

    partner_id = fields.Many2one(
        'res.partner',
        string='Client Company',
        required=True,
        ondelete='cascade',
        domain="[('is_company', '=', True)]"
    )
    company_id = fields.Many2one(
        'res.company',
        string='Operating Company',
        required=True
    )
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist'
    )
    payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Payment Term'
    )
    incoterm_id = fields.Many2one(
        'account.incoterms',
        string='Incoterm'
    )
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        (
            'btp_partner_company_unique',
            'unique(partner_id, company_id)',
            'Only one commercial condition is allowed per client and operating company.',
        ),
    ]

    @api.constrains('partner_id', 'company_id')
    def _check_partner_company_consistency(self):
        for rec in self:
            if not rec.partner_id or not rec.company_id:
                continue
            if not rec.partner_id.is_company:
                raise ValidationError(_('Commercial conditions can only be set on client companies.'))
            shared_companies = rec.partner_id.btp_shared_company_ids
            if shared_companies and rec.company_id not in shared_companies:
                raise ValidationError(_(
                    'Company "%s" is not in the client shared companies list.'
                ) % rec.company_id.name)
            if shared_companies and not rec.company_id.btp_shared_clients:
                raise ValidationError(_(
                    'Company "%s" has "Use Shared Clients" disabled. Enable it before adding shared client conditions.'
                ) % rec.company_id.name)

