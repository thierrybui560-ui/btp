# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 9 — Stocks & Logistics

from odoo import api, fields, models


class StockMove(models.Model):
    """Extend stock move for BTP: site link and origin type for traceability and reporting."""
    _inherit = 'stock.move'

    btp_site_id = fields.Many2one(
        'project.project',
        string='Site',
        ondelete='set null',
        index=True,
        domain=[('btp_site_code', '!=', False)],
        help='Site concerned by this move (consumption, transfer to site, etc.).',
    )
    btp_origin_type = fields.Selection(
        [
            ('supplier_order', 'Supplier Order'),
            ('client_order', 'Client Order'),
            ('site_consumption', 'Site Consumption'),
            ('transfer', 'Internal Transfer'),
            ('return', 'Return to Supplier'),
            ('loss', 'Loss / Waste'),
        ],
        string='BTP Origin',
        help='Business origin of the move for BTP reporting.',
    )
    btp_consumption_id = fields.Many2one(
        'btp.site.consumption',
        string='Site Consumption',
        ondelete='set null',
        index=True,
        help='When origin is site consumption: linked BTP consumption record.',
    )

    def _action_done(self, cancel_backorder=False):
        """When a move linked to a BTP consumption is done, sync real_qty on the consumption."""
        res = super()._action_done(cancel_backorder=cancel_backorder)
        for move in self:
            if move.btp_consumption_id and move.state == 'done':
                move.btp_consumption_id.real_qty = move.quantity
        return res
