# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='partner_id.company_id',
        store=True,
        readonly=True,
        index=True,
    )
    old_user_id = fields.Many2one('res.users', string='Previous Salesperson')
    new_user_id = fields.Many2one('res.users', string='New Salesperson')
    changed_by_id = fields.Many2one('res.users', string='Changed By', required=True)
    change_date = fields.Datetime(string='Change Date', default=fields.Datetime.now, required=True)
    reason = fields.Text(string='Reason', help='Reason for reattribution (who, when, why).')

    @api.constrains('reason')
    def _check_reason_required(self):
        for rec in self:
            if not (rec.reason or '').strip():
                raise ValidationError(_('Reattribution reason is required for governance traceability.'))

