# -*- coding: utf-8 -*-

from odoo.tests.common import SavepointCase


class TestBtpAiScoring(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Lead = cls.env['btp.lead']

    def test_manual_ai_rescore_creates_log(self):
        lead = self.Lead.create({
            'name': 'AI scoring test lead',
            'origin': 'web',
            'probability': 40.0,
        })
        lead.action_ai_rescore()
        self.assertGreaterEqual(lead.ai_score, 0.0)
        self.assertLessEqual(lead.ai_score, 100.0)
        self.assertTrue(lead.ai_last_scored_at)
        logs = self.env['btp.lead.score.log'].search([('lead_id', '=', lead.id)])
        self.assertTrue(logs)
