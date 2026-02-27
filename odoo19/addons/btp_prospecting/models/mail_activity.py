# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 12 — Third Parties & Integrated Messaging

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    btp_escalated = fields.Boolean(
        string='Escalated to Manager',
        default=False,
        help='Set when this overdue activity has been escalated to N+1.',
    )

    @api.model
    def _cron_btp_escalate_overdue_activities(self):
        """Escalate overdue activities to the assignee's manager (N+1)."""
        today = fields.Date.context_today(self)
        overdue = self.search([
            ('date_deadline', '<', today),
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
