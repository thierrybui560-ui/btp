# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class BtpSitePointing(models.Model):
    _name = 'btp.site.pointing'
    _description = 'Site Pointing Entry'
    _order = 'date desc, site_id, task_id, id desc'

    site_id = fields.Many2one('project.project', string='Site', required=True, ondelete='cascade', index=True)
    task_id = fields.Many2one('project.task', string='Task', ondelete='set null', index=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today, index=True)
    user_id = fields.Many2one('res.users', string='Employee', ondelete='cascade', index=True, domain=[('share', '=', False)])
    subcontractor_id = fields.Many2one('res.partner', string='Subcontractor', ondelete='cascade', index=True,
        domain="[('is_company', '=', True), ('is_subcontractor', '=', True)]")
    hours = fields.Float(string='Hours', digits=(16, 2), default=0.0)
    qty_done = fields.Float(string='Quantity Done', digits='Product Unit of Measure', default=0.0)
    uom_id = fields.Many2one('uom.uom', string='Unit')
    notes = fields.Text(string='Notes')

    @api.constrains('user_id', 'subcontractor_id')
    def _check_employee_or_subcontractor(self):
        for r in self:
            if not r.user_id and not r.subcontractor_id:
                raise ValidationError(_('Please set either Employee or Subcontractor.'))
            if r.user_id and r.subcontractor_id:
                raise ValidationError(_('Set either Employee or Subcontractor, not both.'))
