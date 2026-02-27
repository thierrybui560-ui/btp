# -*- coding: utf-8 -*-
# Module 9: propagation of BTP site to stock moves from sale order.

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    btp_item_id = fields.Many2one(
        'btp.quote.item',
        string='BTP Quote Item',
        ondelete='set null',
        index=True
    )
    btp_lot_id = fields.Many2one(
        'btp.quote.lot',
        string='BTP Lot',
        related='btp_item_id.lot_id',
        store=True,
        readonly=True,
        index=True
    )
    btp_title_id = fields.Many2one(
        'btp.quote.title',
        string='BTP Title',
        related='btp_item_id.title_id',
        store=True,
        readonly=True,
        index=True
    )
    btp_subtitle_id = fields.Many2one(
        'btp.quote.subtitle',
        string='BTP Subtitle',
        related='btp_item_id.subtitle_id',
        store=True,
        readonly=True,
        index=True
    )

    def _prepare_procurement_values(self):
        """Propagate BTP site and origin to stock moves created from this line (Module 9)."""
        values = super()._prepare_procurement_values()
        if self.order_id.btp_site_id:
            values['btp_site_id'] = self.order_id.btp_site_id.id
            values['btp_origin_type'] = 'client_order'
        return values

