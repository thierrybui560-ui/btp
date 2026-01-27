# -*- coding: utf-8 -*-

from odoo import models, fields


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

