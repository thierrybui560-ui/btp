# -*- coding: utf-8 -*-

from odoo import fields, models


class BtpLeadScoreLog(models.Model):
    _name = 'btp.lead.score.log'
    _description = 'BTP Lead AI Score Log'
    _order = 'scored_at desc, id desc'

    lead_id = fields.Many2one('btp.lead', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='lead_id.company_id',
        store=True,
        readonly=True,
        index=True,
    )
    score = fields.Float(digits=(12, 2), required=True)
    reason = fields.Text()
    scored_at = fields.Datetime(default=fields.Datetime.now, required=True)
    model_info = fields.Char(help='Model/provider identifier used for scoring (if any).')
