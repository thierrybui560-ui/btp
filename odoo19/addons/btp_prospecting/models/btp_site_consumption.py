# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BtpSiteConsumption(models.Model):
    """Article consumption on site: planned (from quote) vs actual, with variance and overconsumption alert."""
    _name = 'btp.site.consumption'
    _description = 'Site Article Consumption'
    _order = 'site_id, product_id, id'

    site_id = fields.Many2one(
        'project.project',
        string='Site',
        required=True,
        ondelete='cascade',
        index=True,
        help='Site this consumption belongs to.'
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        ondelete='set null',
        index=True,
        help='Task (quote item) this consumption is for.'
    )
    quote_item_id = fields.Many2one(
        'btp.quote.item',
        string='Quote Item',
        ondelete='set null',
        index=True,
        help='Quote item (for planned quantity reference).'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Article',
        required=True,
        ondelete='restrict',
        domain=[('type', '=', 'consu')],
        index=True,
        help='Consumed article (product).'
    )
    planned_qty = fields.Float(
        string='Planned Quantity',
        digits='Product Unit of Measure',
        default=0.0,
        help='Quantity planned from quote (from quote item articles).'
    )
    real_qty = fields.Float(
        string='Actual Quantity',
        digits='Product Unit of Measure',
        default=0.0,
        help='Actual quantity consumed on site.'
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit',
        related='product_id.uom_id',
        store=True,
        readonly=True
    )
    variance = fields.Float(
        string='Variance',
        digits='Product Unit of Measure',
        compute='_compute_variance',
        store=True,
        help='Real - Planned (positive = overconsumption).'
    )
    overconsumption_alert = fields.Boolean(
        string='Overconsumption Alert',
        compute='_compute_overconsumption_alert',
        store=True,
        help='True if actual consumption exceeds planned.'
    )
    notes = fields.Text(string='Notes')

    @api.depends('planned_qty', 'real_qty')
    def _compute_variance(self):
        for r in self:
            r.variance = r.real_qty - r.planned_qty

    @api.depends('variance')
    def _compute_overconsumption_alert(self):
        for r in self:
            r.overconsumption_alert = r.planned_qty > 0 and r.variance > 0
