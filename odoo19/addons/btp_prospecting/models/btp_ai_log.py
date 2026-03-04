# -*- coding: utf-8 -*-

from odoo import fields, models


class BtpAiLog(models.Model):
    _name = 'btp.ai.log'
    _description = 'BTP AI Execution Log'
    _order = 'id desc'

    provider_id = fields.Many2one('btp.ai.provider', ondelete='set null')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        index=True,
    )
    model_name = fields.Char()
    status = fields.Selection(
        [('running', 'Running'), ('done', 'Done'), ('failed', 'Failed')],
        default='running',
    )
    prompt = fields.Text()
    system_prompt = fields.Text()
    response = fields.Text()
    response_payload = fields.Text()
    error_message = fields.Text()
    started_at = fields.Datetime()
    finished_at = fields.Datetime()
