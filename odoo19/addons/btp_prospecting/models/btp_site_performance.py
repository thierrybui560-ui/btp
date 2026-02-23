# -*- coding: utf-8 -*-
from odoo import api, fields, models

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
