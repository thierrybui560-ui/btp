# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.tests.common import SavepointCase


class TestBtpYieldEscalation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env['project.project'].create({'name': 'Yield Site'})
        cls.task = cls.env['project.task'].create({
            'name': 'Yield Task',
            'project_id': cls.project.id,
        })

    def test_low_yield_escalation_cron(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'btp_prospecting.btp_yield_escalation_days', '0'
        )
        perf = self.env['btp.site.performance'].create({
            'task_id': self.task.id,
            'date': fields.Date.today() - timedelta(days=1),
            'expected_qty': 100.0,
            'real_qty': 40.0,
        })
        self.assertTrue(perf.yield_alert)
        count = self.env['btp.site.performance']._cron_escalate_low_yield()
        self.assertGreaterEqual(count, 1)
        activities = self.env['mail.activity'].search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', self.project.id),
            ('summary', 'ilike', 'Low yield escalation'),
        ])
        self.assertTrue(activities)
