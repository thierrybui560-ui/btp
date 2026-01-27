# -*- coding: utf-8 -*-

from odoo import models, fields


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

