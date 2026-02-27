# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 9 — Stocks & Logistics

from odoo import models


class StockRule(models.Model):
    """Extend stock rule so moves created from procurement get BTP fields from values."""
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        """Pass BTP site and origin from procurement values to the created stock move."""
        res = super()._get_custom_move_fields()
        return res + ['btp_site_id', 'btp_origin_type']
