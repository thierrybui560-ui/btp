# -*- coding: utf-8 -*-

from odoo import fields, models


class BtpTenderSource(models.Model):
    _name = 'btp.tender.source'
    _description = 'BTP Tender Source'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        index=True,
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    source_type = fields.Selection(
        [('rss', 'RSS Feed'), ('json_api', 'JSON API')],
        required=True,
        default='rss',
    )
    url = fields.Char(required=True)
    default_company_id = fields.Many2one('res.company')
    default_open_mode = fields.Boolean(
        default=True,
        help='If enabled, tenders are created as common open leads.',
    )
    last_fetch_at = fields.Datetime(readonly=True)
