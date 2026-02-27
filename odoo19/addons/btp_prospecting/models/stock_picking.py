# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 9 — Stocks & Logistics

from odoo import api, fields, models


class StockPicking(models.Model):
    """Extend picking for BTP: site from first move for traceability."""
    _inherit = 'stock.picking'

    btp_site_id = fields.Many2one(
        'project.project',
        string='BTP Site',
        compute='_compute_btp_site_id',
        store=True,
        readonly=True,
        index=True,
        domain=[('btp_site_code', '!=', False)],
        help='Site linked to this transfer (from the first move with a BTP site).',
    )

    @api.depends('move_ids.btp_site_id')
    def _compute_btp_site_id(self):
        for p in self:
            site = p.move_ids.filtered('btp_site_id')[:1].btp_site_id
            p.btp_site_id = site
