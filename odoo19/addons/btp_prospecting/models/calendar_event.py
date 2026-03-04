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
        if self.env.context.get('btp_skip_res_sync'):
            return super().write(vals)
        res = super().write(vals)
        if 'btp_site_id' in vals or 'btp_lead_id' in vals:
            site_model_id = self.env['ir.model']._get('project.project').id
            lead_model_id = self.env['ir.model']._get('btp.lead').id
            for event in self:
                if event.btp_site_id:
                    target_vals = {
                        'res_model_id': site_model_id,
                        'res_id': event.btp_site_id.id,
                    }
                elif event.btp_lead_id:
                    target_vals = {
                        'res_model_id': lead_model_id,
                        'res_id': event.btp_lead_id.id,
                    }
                else:
                    target_vals = {
                        'res_model_id': False,
                        'res_id': False,
                    }
                super(CalendarEvent, event.with_context(btp_skip_res_sync=True)).write(target_vals)
        return res
