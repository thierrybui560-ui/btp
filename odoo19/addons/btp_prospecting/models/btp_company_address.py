# -*- coding: utf-8 -*-

from odoo import models, fields


class BtpCompanyAddress(models.Model):
    _name = 'btp.company.address'
    _description = 'BTP Company Address'
    _order = 'address_type, id desc'

    partner_id = fields.Many2one(
        'res.partner',
        string='Company',
        required=True,
        ondelete='cascade',
        domain="[('is_company', '=', True)]"
    )
    address_type = fields.Selection(
        [
            ('hq', 'Headquarters'),
            ('agency', 'Agency'),
            ('site', 'Site'),
            ('other', 'Other'),
        ],
        string='Address Type',
        required=True,
        default='hq'
    )
    name = fields.Char(string='Label')
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    zip = fields.Char(string='ZIP')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    active = fields.Boolean(default=True)

