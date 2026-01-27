# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class BtpArticlePriceHistory(models.Model):
    """Purchase price history for articles by supplier"""
    _name = 'btp.article.price.history'
    _description = 'Article Price History'
    _order = 'article_id, supplier_id, purchase_date desc'

    article_id = fields.Many2one(
        'product.template',
        string='Article',
        required=True,
        ondelete='cascade',
        index=True
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        required=True,
        # Domain will be applied after module upgrade completes
        ondelete='cascade',
        index=True
    )
    purchase_date = fields.Date(
        string='Purchase Date',
        required=True,
        default=fields.Date.today,
        help='Date of purchase'
    )
    purchase_price = fields.Float(
        string='Purchase Price',
        required=True,
        digits='Product Price',
        help='Price paid to the supplier'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        digits='Product Unit of Measure',
        help='Quantity purchased'
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        related='article_id.uom_id',
        store=True,
        readonly=True
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        help='Related purchase order (if any)'
    )
    notes = fields.Text(
        string='Notes',
        help='Additional notes about this purchase'
    )

    @api.constrains('purchase_price')
    def _check_price(self):
        for record in self:
            if record.purchase_price <= 0:
                raise ValidationError(_('Purchase price must be positive.'))

