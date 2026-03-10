# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 12 — Third Parties & Integrated Messaging

from odoo import models, fields, api, _


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
    btp_call_report_ids = fields.One2many(
        'btp.call.report',
        'calendar_event_id',
        string='Call / Meeting Reports',
        readonly=True,
    )
    btp_call_report_count = fields.Integer(
        string='Reports',
        compute='_compute_btp_call_report_count',
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
        events = super().create(vals_list)
        events._btp_schedule_missing_report_activity()
        return events

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
        self._btp_schedule_missing_report_activity()
        return res

    @api.depends('btp_call_report_ids')
    def _compute_btp_call_report_count(self):
        for event in self:
            event.btp_call_report_count = len(event.btp_call_report_ids)

    def action_btp_open_reports(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Meeting Reports'),
            'res_model': 'btp.call.report',
            'view_mode': 'list,form',
            'domain': [('calendar_event_id', '=', self.id)],
            'context': {
                'default_calendar_event_id': self.id,
                'default_report_type': 'meeting',
                'default_name': self.name or _('Meeting follow-up'),
                'default_partner_id': self.partner_ids[:1].id if self.partner_ids else False,
                'default_btp_site_id': self.btp_site_id.id if self.btp_site_id else False,
                'default_btp_lead_id': self.btp_lead_id.id if self.btp_lead_id else False,
                'default_date': self.start,
            },
        }

    def action_btp_create_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Meeting Report'),
            'res_model': 'btp.call.report',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_calendar_event_id': self.id,
                'default_report_type': 'meeting',
                'default_name': self.name or _('Meeting follow-up'),
                'default_partner_id': self.partner_ids[:1].id if self.partner_ids else False,
                'default_btp_site_id': self.btp_site_id.id if self.btp_site_id else False,
                'default_btp_lead_id': self.btp_lead_id.id if self.btp_lead_id else False,
                'default_date': self.start,
            },
        }

    def _btp_schedule_missing_report_activity(self):
        """Create one reminder activity when a past BTP meeting has no report."""
        todo_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not todo_type:
            todo_type = self.env['mail.activity.type'].search([('category', '=', 'default')], limit=1)
        model = self.env['ir.model']._get('calendar.event')
        now = fields.Datetime.now()
        for event in self:
            if not (event.btp_site_id or event.btp_lead_id):
                continue
            if event.btp_call_report_ids:
                continue
            if not event.stop or event.stop > now:
                continue
            existing = self.env['mail.activity'].search_count([
                ('res_model_id', '=', model.id),
                ('res_id', '=', event.id),
                ('summary', '=', 'BTP mandatory meeting report'),
            ])
            if existing:
                continue
            self.env['mail.activity'].create({
                'activity_type_id': (todo_type or self.env['mail.activity.type'].search([], limit=1)).id,
                'summary': 'BTP mandatory meeting report',
                'note': _('Create and complete the call/meeting report for this BTP-linked appointment.'),
                'date_deadline': fields.Date.context_today(self),
                'user_id': (event.user_id or self.env.user).id,
                'res_model_id': model.id,
                'res_id': event.id,
            })
