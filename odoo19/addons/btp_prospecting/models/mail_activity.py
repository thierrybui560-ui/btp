# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 12 — Third Parties & Integrated Messaging

import logging
from datetime import timedelta

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    btp_escalated = fields.Boolean(
        string='Escalated to Manager',
        default=False,
        help='Set when this overdue activity has been escalated to N+1.',
    )
    btp_reminder_d_sent = fields.Boolean(
        string='D Reminder Sent',
        default=False,
        help='Reminder sent on deadline day.',
    )
    btp_reminder_d15_sent = fields.Boolean(
        string='D+15 Reminder Sent',
        default=False,
        help='Reminder sent 15 days after deadline.',
    )
    btp_reminder_d30_sent = fields.Boolean(
        string='D+30 Reminder Sent',
        default=False,
        help='Reminder sent 30 days after deadline.',
    )

    @api.model
    def _cron_btp_escalate_overdue_activities(self):
        """Escalate overdue activities to the assignee's manager (N+1) at D+30."""
        # Keep a single scheduler entry practical: run reminder milestones before escalation.
        self._cron_btp_send_activity_reminders()
        today = fields.Date.context_today(self)
        escalation_threshold = today - timedelta(days=30)
        overdue = self.search([
            ('date_deadline', '<=', escalation_threshold),
            ('btp_escalated', '=', False),
            ('user_id.manager_id', '!=', False),
        ])
        todo_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not todo_type:
            todo_type = self.env['mail.activity.type'].search([('category', '=', 'default')], limit=1)
        for activity in overdue:
            try:
                manager = activity.user_id.manager_id
                if not manager or not activity.res_model or not activity.res_id:
                    continue
                self.env['mail.activity'].create({
                    'activity_type_id': (todo_type or self.env['mail.activity.type'].search([], limit=1)).id,
                    'summary': _('Escalation: Overdue – %s (was %s)') % (activity.summary or _('Task'), activity.user_id.name),
                    'date_deadline': today,
                    'user_id': manager.id,
                    'res_model_id': activity.res_model_id.id,
                    'res_id': activity.res_id,
                    'note': _('Original deadline was %s. Assignee: %s.') % (activity.date_deadline, activity.user_id.name),
                })
                activity.btp_escalated = True
                _logger.info('BTP: Escalated overdue activity %s to manager %s', activity.id, manager.name)
            except Exception as e:
                _logger.exception('BTP escalation failed for activity %s: %s', activity.id, e)

    @api.model
    def _cron_btp_send_activity_reminders(self):
        """Send reminder milestones for open activities: D, D+15, D+30."""
        today = fields.Date.context_today(self)
        activities = self.search([
            ('date_deadline', '!=', False),
            ('user_id', '!=', False),
        ])
        for activity in activities:
            delay = (today - activity.date_deadline).days
            if delay >= 30 and not activity.btp_reminder_d30_sent:
                self._btp_send_reminder_notice(activity, 'D+30')
                activity.btp_reminder_d30_sent = True
            elif delay >= 15 and not activity.btp_reminder_d15_sent:
                self._btp_send_reminder_notice(activity, 'D+15')
                activity.btp_reminder_d15_sent = True
            elif delay == 0 and not activity.btp_reminder_d_sent:
                self._btp_send_reminder_notice(activity, 'D')
                activity.btp_reminder_d_sent = True

    @api.model
    def _btp_send_reminder_notice(self, activity, stage):
        """Notify assignee and keep a reminder trace in chatter."""
        model = self.env[activity.res_model] if activity.res_model else False
        target = model.browse(activity.res_id) if model and activity.res_id else False
        summary = activity.summary or _('Task')
        note = _('Reminder %s: "%s" deadline is %s.') % (stage, summary, activity.date_deadline)
        if target and hasattr(target, 'message_post'):
            target.message_post(body=note, message_type='comment')
        if activity.user_id and activity.user_id.email:
            self.env['mail.mail'].sudo().create({
                'subject': _('BTP Reminder %s: %s') % (stage, summary),
                'body_html': '<p>%s</p>' % note,
                'email_to': activity.user_id.email,
            }).send()
