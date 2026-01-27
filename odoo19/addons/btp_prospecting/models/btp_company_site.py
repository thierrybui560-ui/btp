# -*- coding: utf-8 -*-

from odoo import models, fields


class BtpCompanySite(models.Model):
    _name = 'btp.company.site'
    _description = 'BTP Company Site'
    _order = 'name'

    name = fields.Char(string='Site Name', required=True)
    agency_id = fields.Many2one(
        'btp.company.agency',
        string='Agency',
        required=True
    )
    company_id = fields.Many2one(
        'res.partner',
        string='Company',
        required=True,
        domain="[('is_company', '=', True)]"
    )
    contact_ids = fields.Many2many(
        'res.partner',
        'btp_site_contact_rel',
        'site_id',
        'contact_id',
        string='Contacts',
        domain="[('is_company', '=', False)]"
    )
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    zip = fields.Char(string='ZIP')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

