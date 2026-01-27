# -*- coding: utf-8 -*-

from odoo import models, fields


class BtpCompanyReattribution(models.Model):
    _name = 'btp.company.reattribution'
    _description = 'BTP Company Reattribution History'
    _order = 'change_date desc, id desc'

    partner_id = fields.Many2one(
        'res.partner',
        string='Company/Contact',
        required=True,
        ondelete='cascade'
    )
    old_user_id = fields.Many2one('res.users', string='Previous Salesperson')
    new_user_id = fields.Many2one('res.users', string='New Salesperson')
    changed_by_id = fields.Many2one('res.users', string='Changed By', required=True)
    change_date = fields.Datetime(string='Change Date', default=fields.Datetime.now, required=True)

