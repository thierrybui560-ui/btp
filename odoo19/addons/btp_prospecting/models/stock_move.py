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

    def _btp_guess_site_id(self):
        """Best-effort site inference from picking and locations."""
        self.ensure_one()
        site = (
            self.btp_site_id
            or self.picking_id.btp_site_id
            or self.location_dest_id.btp_site_id
            or self.location_id.btp_site_id
        )
        return site.id if site else False

    def _btp_guess_origin_type(self):
        """Best-effort origin inference to keep movement traceability consistent."""
        self.ensure_one()
        if self.btp_consumption_id:
            return 'site_consumption'
        if self.sale_line_id:
            return 'client_order'
        if self.purchase_line_id:
            return 'supplier_order'
        if self.origin_returned_move_id:
            return 'return'
        # Odoo 19 no longer exposes `stock.location.scrap_location` on locations.
        # Detect losses/scrap from move metadata instead.
        if self.scrap_id or self.location_dest_usage == 'inventory':
            return 'loss'
        if self.picking_type_id:
            if self.picking_type_id.code == 'internal':
                return 'transfer'
            if self.picking_type_id.code == 'incoming':
                return 'supplier_order'
        return False

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-fill missing BTP traceability fields on creation."""
        moves = super().create(vals_list)
        for move, vals in zip(moves, vals_list):
            update_vals = {}
            if not vals.get('btp_site_id'):
                site_id = move._btp_guess_site_id()
                if site_id:
                    update_vals['btp_site_id'] = site_id
            if not vals.get('btp_origin_type'):
                origin_type = move._btp_guess_origin_type()
                if origin_type:
                    update_vals['btp_origin_type'] = origin_type
            if update_vals:
                move.with_context(btp_skip_traceability_sync=True).write(update_vals)
        return moves

    def write(self, vals):
        """Backfill BTP traceability when move changes and fields are empty."""
        if self.env.context.get('btp_skip_traceability_sync'):
            return super().write(vals)

        res = super().write(vals)
        for move in self:
            update_vals = {}
            if not move.btp_site_id:
                site_id = move._btp_guess_site_id()
                if site_id:
                    update_vals['btp_site_id'] = site_id
            if not move.btp_origin_type:
                origin_type = move._btp_guess_origin_type()
                if origin_type:
                    update_vals['btp_origin_type'] = origin_type
            if update_vals:
                move.with_context(btp_skip_traceability_sync=True).write(update_vals)
        return res

    def unlink(self):
        """Detach linked consumptions before deleting stock moves.

        Some environments may keep restrictive FK behavior on custom links; clearing
        the pointer first avoids validation errors while preserving data consistency.
        """
        consumptions = self.env['btp.site.consumption'].search([('stock_move_id', 'in', self.ids)])
        if consumptions:
            consumptions.write({'stock_move_id': False})
        return super().unlink()

    def _action_done(self, cancel_backorder=False):
        """When a move linked to a BTP consumption is done, sync real_qty on the consumption."""
        res = super()._action_done(cancel_backorder=cancel_backorder)
        for move in self:
            if move.btp_consumption_id and move.state == 'done':
                move.btp_consumption_id.real_qty = move.quantity
        return res
