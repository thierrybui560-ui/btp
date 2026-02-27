# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 12 — Third Parties & Integrated Messaging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

REPORT_TYPE = [
    ('call', 'Call'),
    ('meeting', 'Meeting'),
]


class BtpCallReport(models.Model):
    _name = 'btp.call.report'
    _description = 'Call / Meeting Report'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Subject',
        required=True,
        tracking=True,
    )
    report_type = fields.Selection(
        REPORT_TYPE,
        string='Type',
        required=True,
        default='call',
        tracking=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Third Party',
        required=True,
        ondelete='cascade',
        tracking=True,
        help='Client, supplier, or subcontractor.',
    )
    btp_site_id = fields.Many2one(
        'project.project',
        string='Site',
        ondelete='set null',
        tracking=True,
        domain=[('btp_site_code', '!=', False)],
    )
    btp_lead_id = fields.Many2one(
        'btp.lead',
        string='Lead / Opportunity',
        ondelete='set null',
        tracking=True,
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Quote / Order',
        ondelete='set null',
        tracking=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Reported By',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    date = fields.Datetime(
        string='Date',
        default=fields.Datetime.now,
        required=True,
        tracking=True,
    )
    duration_minutes = fields.Integer(
        string='Duration (min)',
        help='Call or meeting duration in minutes.',
    )
    interlocutor = fields.Char(
        string='Interlocutor',
        help='Person spoken to (for calls).',
    )
    summary = fields.Text(
        string='Summary',
        tracking=True,
    )
    decision = fields.Text(
        string='Decision / Outcome',
        help='Decision made or outcome of the call/meeting.',
    )
    action_ids = fields.One2many(
        'btp.call.report.action',
        'call_report_id',
        string='Follow-up Actions',
        copy=True,
    )
    calendar_event_id = fields.Many2one(
        'calendar.event',
        string='Linked Meeting',
        ondelete='set null',
        readonly=True,
        help='Meeting event this report is linked to (if any).',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    def action_create_tasks(self):
        """Create mail activities (tasks) from action lines and open the third party form."""
        self.ensure_one()
        todo_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not todo_type:
            todo_type = self.env['mail.activity.type'].search([('category', '=', 'default')], limit=1)
        for line in self.action_ids:
            if line.mail_activity_id:
                continue
            if not line.deadline_date:
                raise UserError(_('Each follow-up action must have a deadline. Please set a deadline for: %s') % (line.name or _('Action')))
            activity_vals = {
                'activity_type_id': todo_type.id if todo_type else self.env['mail.activity.type'].search([], limit=1).id,
                'summary': line.name or _('Follow-up'),
                'date_deadline': line.deadline_date,
                'user_id': (line.assigned_to_id or self.env.user).id,
                'res_model_id': self.env['ir.model']._get('res.partner').id,
                'res_id': self.partner_id.id,
            }
            if line.note:
                activity_vals['note'] = line.note
            activity = self.env['mail.activity'].create(activity_vals)
            line.mail_activity_id = activity.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': self.partner_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class BtpCallReportAction(models.Model):
    _name = 'btp.call.report.action'
    _description = 'Call/Meeting Follow-up Action'

    call_report_id = fields.Many2one(
        'btp.call.report',
        string='Report',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(string='Action', required=True)
    note = fields.Text(string='Details')
    assigned_to_id = fields.Many2one(
        'res.users',
        string='Assigned To',
        default=lambda self: self.env.user,
    )
    deadline_date = fields.Date(string='Deadline')
    mail_activity_id = fields.Many2one(
        'mail.activity',
        string='Task',
        readonly=True,
        ondelete='set null',
    )
