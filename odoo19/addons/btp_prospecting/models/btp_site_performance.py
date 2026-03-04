# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, _

class BtpSitePerformance(models.Model):
    _name = 'btp.site.performance'
    _description = 'Site Yield Entry'
    _order = 'date desc, task_id, id desc'

    task_id = fields.Many2one('project.task', string='Task', required=True, ondelete='cascade', index=True)
    project_id = fields.Many2one('project.project', string='Site', related='task_id.project_id', store=True, readonly=True, index=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today, index=True)
    expected_qty = fields.Float(string='Expected Qty', digits=(16, 2), default=0.0)
    real_qty = fields.Float(string='Actual Qty', digits=(16, 2), default=0.0)
    uom_id = fields.Many2one('uom.uom', string='Unit')
    performance_rate = fields.Float(string='Yield Rate %', digits=(12, 2), compute='_compute_performance_rate', store=True)
    yield_alert = fields.Boolean(compute='_compute_yield_alert', store=True)
    notes = fields.Text()

    @api.depends('expected_qty', 'real_qty')
    def _compute_performance_rate(self):
        for r in self:
            if r.expected_qty and r.expected_qty != 0:
                r.performance_rate = (r.real_qty / r.expected_qty) * 100.0
            else:
                r.performance_rate = 100.0 if r.real_qty == 0 else 0.0

    def _get_yield_alert_threshold(self):
        p = self.env['ir.config_parameter'].sudo().get_param('btp_prospecting.btp_yield_alert_threshold', '80')
        try:
            return float(p)
        except (TypeError, ValueError):
            return 80.0

    @api.depends('performance_rate')
    def _compute_yield_alert(self):
        t = self._get_yield_alert_threshold()
        for r in self:
            r.yield_alert = bool(r.expected_qty and r.performance_rate < t)

    @api.model
    def _cron_escalate_low_yield(self):
        """Create management activities when low-yield alerts stay unresolved."""
        ICP = self.env['ir.config_parameter'].sudo()
        try:
            wait_days = int(ICP.get_param('btp_prospecting.btp_yield_escalation_days', 2))
        except (TypeError, ValueError):
            wait_days = 2
        threshold = fields.Date.today() - timedelta(days=max(wait_days, 0))
        domain = [
            ('yield_alert', '=', True),
            ('date', '<=', threshold),
        ]
        rows = self.search(domain)
        if not rows:
            return 0
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return 0
        created = 0
        for rec in rows:
            site = rec.project_id
            assignee = site.user_id.manager_id or site.user_id or self.env.user
            summary = _('Low yield escalation: %s') % (site.display_name,)
            existing = self.env['mail.activity'].search([
                ('res_model', '=', 'project.project'),
                ('res_id', '=', site.id),
                ('activity_type_id', '=', activity_type.id),
                ('summary', '=', summary),
            ], limit=1)
            if existing:
                continue
            note = _(
                'Yield is below threshold for task "%(task)s".\n'
                'Expected: %(expected).2f\n'
                'Actual: %(actual).2f\n'
                'Rate: %(rate).2f%%\n'
                'Recorded on: %(date)s'
            ) % {
                'task': rec.task_id.display_name,
                'expected': rec.expected_qty or 0.0,
                'actual': rec.real_qty or 0.0,
                'rate': rec.performance_rate or 0.0,
                'date': rec.date,
            }
            self.env['mail.activity'].create({
                'res_model': 'project.project',
                'res_id': site.id,
                'activity_type_id': activity_type.id,
                'summary': summary,
                'note': note,
                'date_deadline': fields.Date.today(),
                'user_id': assignee.id,
            })
            created += 1
        return created
