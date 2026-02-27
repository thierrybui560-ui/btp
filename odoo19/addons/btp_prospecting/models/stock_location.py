# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 9 — Stocks & Logistics

from odoo import api, fields, models


class StockLocation(models.Model):
    """Extend location for BTP: link to site for site depots."""
    _inherit = 'stock.location'

    btp_site_id = fields.Many2one(
        'project.project',
        string='Site',
        ondelete='set null',
        index=True,
        domain=[('btp_site_code', '!=', False)],
        help='When this location is a site depot (or sublocation of one), the linked site.',
    )
