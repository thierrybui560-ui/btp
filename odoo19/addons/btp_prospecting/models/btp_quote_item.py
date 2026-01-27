# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class BtpQuoteItem(models.Model):
    """Quote Item - Base unit representing a billable service"""
    _name = 'btp.quote.item'
    _description = 'Quote Item'
    _order = 'subtitle_id, sequence, name'

    name = fields.Char(
        string='Item Name',
        required=True,
        help='Name of the item (e.g., Application flocking thickness 3 cm)'
    )
    subtitle_id = fields.Many2one(
        'btp.quote.subtitle',
        string='Subtitle',
        required=True,
        ondelete='cascade',
        index=True
    )
    title_id = fields.Many2one(
        'btp.quote.title',
        string='Title',
        related='subtitle_id.title_id',
        store=True,
        readonly=True,
        index=True
    )
    lot_id = fields.Many2one(
        'btp.quote.lot',
        string='Lot',
        related='subtitle_id.lot_id',
        store=True,
        readonly=True,
        index=True
    )
    quote_id = fields.Many2one(
        'sale.order',
        string='Quote',
        related='subtitle_id.quote_id',
        store=True,
        readonly=True,
        index=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display within the subtitle'
    )
    description = fields.Text(
        string='Description',
        help='Description of the item'
    )
    btp_sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        copy=False,
        ondelete='set null',
        help='Linked sales order line for pricing and totals'
    )

    # ========== Articles (Raw Materials, Supplies) ==========
    article_ids = fields.One2many(
        'btp.quote.item.article',
        'item_id',
        string='Articles',
        help='Articles (raw materials, supplies) used in this item'
    )
    article_count = fields.Integer(
        string='Articles Count',
        compute='_compute_article_count',
        store=True
    )

    # ========== Labor ==========
    labor_ids = fields.One2many(
        'btp.quote.item.labor',
        'item_id',
        string='Labor',
        help='Labor costs (internal yield or subcontracting)'
    )
    labor_count = fields.Integer(
        string='Labor Count',
        compute='_compute_labor_count',
        store=True
    )

    # ========== Pricing ==========
    article_total_cost = fields.Float(
        string='Articles Total Cost',
        digits='Product Price',
        compute='_compute_totals',
        store=True,
        help='Total cost of all articles'
    )
    labor_total_cost = fields.Float(
        string='Labor Total Cost',
        digits='Product Price',
        compute='_compute_totals',
        store=True,
        help='Total cost of all labor'
    )
    total_cost = fields.Float(
        string='Total Cost',
        digits='Product Price',
        compute='_compute_totals',
        store=True,
        help='Total cost (articles + labor)'
    )
    unit_price = fields.Float(
        string='Unit Price',
        digits='Product Price',
        help='Selling price per unit'
    )
    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        digits='Product Unit of Measure',
        help='Quantity of this item'
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        help='Unit of measure (m², ml, piece, etc.)'
    )
    subtotal = fields.Float(
        string='Subtotal',
        digits='Product Price',
        compute='_compute_subtotal',
        store=True,
        help='Subtotal (unit_price * quantity)'
    )
    margin = fields.Float(
        string='Margin',
        digits='Product Price',
        compute='_compute_margin',
        store=True,
        help='Margin (subtotal - total_cost)'
    )
    margin_percent = fields.Float(
        string='Margin %',
        digits=(12, 2),
        compute='_compute_margin',
        store=True,
        help='Margin percentage'
    )

    def _get_btp_item_product(self):
        template = self.env.ref('btp_prospecting.product_btp_quote_item_service_template', raise_if_not_found=False)
        return template.product_variant_id if template else False

    def _prepare_sale_line_vals(self):
        product = self._get_btp_item_product()
        return {
            'order_id': self.quote_id.id,
            'product_id': product.id if product else False,
            'name': self.name,
            'product_uom_qty': self.quantity or 0.0,
            'product_uom_id': self.uom_id.id if self.uom_id else (product.uom_id.id if product else False),
            'price_unit': self.unit_price or 0.0,
            'btp_item_id': self.id,
        }

    def _sync_sale_order_line(self):
        for item in self:
            if not item.quote_id or item.env.context.get('btp_skip_sync'):
                continue
            vals = item._prepare_sale_line_vals()
            if item.btp_sale_line_id:
                item.btp_sale_line_id.with_context(btp_skip_sync=True).write(vals)
            else:
                line = self.env['sale.order.line'].with_context(btp_skip_sync=True).create(vals)
                item.btp_sale_line_id = line.id

    @api.model_create_multi
    def create(self, vals_list):
        items = super(BtpQuoteItem, self).create(vals_list)
        items._sync_sale_order_line()
        return items

    def write(self, vals):
        res = super(BtpQuoteItem, self).write(vals)
        if any(key in vals for key in ['name', 'quantity', 'unit_price', 'uom_id', 'subtitle_id', 'quote_id']):
            self._sync_sale_order_line()
        return res

    def unlink(self):
        for item in self:
            if item.btp_sale_line_id:
                item.btp_sale_line_id.with_context(btp_skip_sync=True).unlink()
        return super(BtpQuoteItem, self).unlink()

    @api.depends('article_ids', 'article_ids.total_cost')
    def _compute_article_count(self):
        for record in self:
            record.article_count = len(record.article_ids)

    @api.depends('labor_ids')
    def _compute_labor_count(self):
        for record in self:
            record.labor_count = len(record.labor_ids)

    @api.depends('article_ids', 'article_ids.total_cost', 'labor_ids', 'labor_ids.total_cost')
    def _compute_totals(self):
        for record in self:
            record.article_total_cost = sum(record.article_ids.mapped('total_cost'))
            record.labor_total_cost = sum(record.labor_ids.mapped('total_cost'))
            record.total_cost = record.article_total_cost + record.labor_total_cost

    @api.depends('unit_price', 'quantity')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.unit_price * record.quantity

    @api.depends('subtotal', 'total_cost')
    def _compute_margin(self):
        for record in self:
            record.margin = record.subtotal - record.total_cost
            if record.subtotal > 0:
                record.margin_percent = (record.margin / record.subtotal) * 100
            else:
                record.margin_percent = 0.0


class BtpQuoteItemArticle(models.Model):
    """Article used in a quote item"""
    _name = 'btp.quote.item.article'
    _description = 'Quote Item Article'
    _order = 'item_id, sequence'

    item_id = fields.Many2one(
        'btp.quote.item',
        string='Item',
        required=True,
        ondelete='cascade',
        index=True
    )
    article_id = fields.Many2one(
        'product.template',
        string='Article',
        required=True,
        domain=[('is_btp_article', '=', True)],
        ondelete='restrict'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0,
        digits='Product Unit of Measure',
        help='Quantity of article needed'
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        related='article_id.uom_id',
        store=True,
        readonly=True
    )
    unit_cost = fields.Float(
        string='Unit Cost',
        digits='Product Price',
        compute='_compute_unit_cost',
        store=True,
        help='Cost per unit (from article average cost or last purchase price)'
    )
    total_cost = fields.Float(
        string='Total Cost',
        digits='Product Price',
        compute='_compute_total_cost',
        store=True,
        help='Total cost (unit_cost * quantity)'
    )
    notes = fields.Text(
        string='Notes',
        help='Additional notes about this article usage'
    )

    @api.depends('article_id', 'article_id.btp_average_cost_price', 'article_id.btp_last_purchase_price')
    def _compute_unit_cost(self):
        for record in self:
            if record.article_id:
                # Use average cost price if available, otherwise last purchase price
                record.unit_cost = (
                    record.article_id.btp_average_cost_price or
                    record.article_id.btp_last_purchase_price or
                    0.0
                )
            else:
                record.unit_cost = 0.0

    @api.depends('unit_cost', 'quantity')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = record.unit_cost * record.quantity


class BtpQuoteItemLabor(models.Model):
    """Labor cost for a quote item (internal yield or subcontracting)"""
    _name = 'btp.quote.item.labor'
    _description = 'Quote Item Labor'
    _order = 'item_id, sequence'

    item_id = fields.Many2one(
        'btp.quote.item',
        string='Item',
        required=True,
        ondelete='cascade',
        index=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    labor_type = fields.Selection([
        ('internal', 'Internal Yield'),
        ('subcontracting', 'Subcontracting'),
    ], string='Labor Type',
        required=True,
        default='internal',
        help='Type of labor calculation'
    )

    # Internal Yield fields
    hourly_cost = fields.Float(
        string='Hourly Cost',
        digits='Product Price',
        help='Hourly cost price for internal labor'
    )
    daily_cost = fields.Float(
        string='Daily Cost',
        digits='Product Price',
        help='Daily cost price for internal labor'
    )
    yield_per_hour = fields.Float(
        string='Yield (per hour)',
        digits='Product Unit of Measure',
        help='Yield in m²/h or ml/h for internal labor'
    )
    yield_per_day = fields.Float(
        string='Yield (per day)',
        digits='Product Unit of Measure',
        help='Yield in m²/day or ml/day for internal labor'
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0,
        digits='Product Unit of Measure',
        help='Quantity to produce (m², ml, piece, etc.)'
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        related='item_id.uom_id',
        store=True,
        readonly=True
    )

    # Subcontracting fields
    subcontractor_id = fields.Many2one(
        'res.partner',
        string='Subcontractor',
        # Domain will be applied after module upgrade completes
        help='Subcontractor for this labor'
    )
    subcontractor_unit_price = fields.Float(
        string='Subcontractor Unit Price',
        digits='Product Price',
        help='Negotiated unit price with subcontractor (m², ml, piece, etc.)'
    )
    subcontractor_quantity = fields.Float(
        string='Subcontractor Quantity',
        digits='Product Unit of Measure',
        help='Quantity for subcontractor'
    )

    # Computed cost
    total_cost = fields.Float(
        string='Total Cost',
        digits='Product Price',
        compute='_compute_total_cost',
        store=True,
        help='Total labor cost'
    )
    notes = fields.Text(
        string='Notes',
        help='Additional notes about this labor'
    )

    @api.depends('labor_type', 'hourly_cost', 'daily_cost', 'yield_per_hour', 'yield_per_day',
                 'quantity', 'subcontractor_unit_price', 'subcontractor_quantity')
    def _compute_total_cost(self):
        for record in self:
            if record.labor_type == 'internal':
                # Calculate based on yield
                if record.yield_per_hour and record.hourly_cost:
                    # Hours needed = quantity / yield_per_hour
                    hours_needed = record.quantity / record.yield_per_hour
                    record.total_cost = hours_needed * record.hourly_cost
                elif record.yield_per_day and record.daily_cost:
                    # Days needed = quantity / yield_per_day
                    days_needed = record.quantity / record.yield_per_day
                    record.total_cost = days_needed * record.daily_cost
                else:
                    record.total_cost = 0.0
            elif record.labor_type == 'subcontracting':
                # Simple: unit_price * quantity
                qty = record.subcontractor_quantity or record.quantity
                record.total_cost = (record.subcontractor_unit_price or 0.0) * qty
            else:
                record.total_cost = 0.0

    @api.onchange('labor_type')
    def _onchange_labor_type(self):
        """Clear fields when switching labor type"""
        if self.labor_type == 'internal':
            self.subcontractor_id = False
            self.subcontractor_unit_price = 0.0
            self.subcontractor_quantity = 0.0
        elif self.labor_type == 'subcontracting':
            self.hourly_cost = 0.0
            self.daily_cost = 0.0
            self.yield_per_hour = 0.0
            self.yield_per_day = 0.0

