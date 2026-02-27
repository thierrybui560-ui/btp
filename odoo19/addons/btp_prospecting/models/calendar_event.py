# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 12 — Third Parties & Integrated Messaging

from odoo import models, fields, api


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    btp_site_id = fields.Many2one(
        'project.project',
        string='BTP Site',
        ondelete='set null',
        help='Link this meeting to a BTP site (project).',
    )
    btp_lead_id = fields.Many2one(
        'btp.lead',
        string='BTP Lead / Opportunity',
        ondelete='set null',
        help='Link this meeting to a BTP lead or opportunity.',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('btp_site_id'):
                vals['res_model_id'] = self.env['ir.model']._get('project.project').id
                vals['res_id'] = vals.get('btp_site_id')
            elif vals.get('btp_lead_id'):
                vals['res_model_id'] = self.env['ir.model']._get('btp.lead').id
                vals['res_id'] = vals.get('btp_lead_id')
        return super().create(vals_list)

    def write(self, vals):
        if 'btp_site_id' in vals and vals['btp_site_id']:
            vals['res_model_id'] = self.env['ir.model']._get('project.project').id
            vals['res_id'] = vals['btp_site_id']
        elif 'btp_lead_id' in vals and vals['btp_lead_id']:
            vals['res_model_id'] = self.env['ir.model']._get('btp.lead').id
            vals['res_id'] = vals['btp_lead_id']
        elif 'btp_site_id' in vals or 'btp_lead_id' in vals:
            vals['res_model_id'] = False
            vals['res_id'] = False
        return super().write(vals)
