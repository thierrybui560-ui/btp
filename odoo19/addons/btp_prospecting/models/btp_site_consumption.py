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
        domain=[('type', 'in', ['consu', 'product'])],
        index=True,
        help='Consumed article (consumable or storable for stock traceability).'
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
    stock_move_id = fields.Many2one(
        'stock.move',
        string='Stock Move',
        ondelete='set null',
        index=True,
        copy=False,
        help='Outbound stock move that fulfilled this consumption (Module 9).',
    )
    notes = fields.Text(string='Notes')

    def _get_quote_item_planned_qty(self, quote_item=None, product=None):
        """Return planned quantity from quote item article lines for a product."""
        self.ensure_one()
        quote_item = quote_item or self.quote_item_id
        product = product or self.product_id
        if not quote_item or not product:
            return 0.0
        product_tmpl = product.product_tmpl_id
        lines = quote_item.article_ids.filtered(lambda l: l.article_id == product_tmpl)
        return sum(lines.mapped('quantity'))

    @api.onchange('quote_item_id', 'product_id')
    def _onchange_quote_item_or_product(self):
        """Pre-fill planned quantity from quote forecast when user did not set one yet."""
        for rec in self:
            if rec.quote_item_id and rec.product_id and not rec.planned_qty:
                planned_qty = rec._get_quote_item_planned_qty()
                if planned_qty > 0:
                    rec.planned_qty = planned_qty

    @api.depends('planned_qty', 'real_qty')
    def _compute_variance(self):
        for r in self:
            r.variance = r.real_qty - r.planned_qty

    @api.depends('variance')
    def _compute_overconsumption_alert(self):
        for r in self:
            r.overconsumption_alert = r.planned_qty > 0 and r.variance > 0

    @api.model_create_multi
    def create(self, vals_list):
        """Default planned quantity from quote item if omitted by user/import."""
        records = self.browse()
        for vals in vals_list:
            if vals.get('planned_qty'):
                continue
            quote_item_id = vals.get('quote_item_id')
            product_id = vals.get('product_id')
            if not quote_item_id or not product_id:
                continue
            quote_item = self.env['btp.quote.item'].browse(quote_item_id)
            product = self.env['product.product'].browse(product_id)
            product_tmpl = product.product_tmpl_id
            planned_qty = sum(
                quote_item.article_ids.filtered(lambda l: l.article_id == product_tmpl).mapped('quantity')
            )
            if planned_qty > 0:
                vals['planned_qty'] = planned_qty
        records = super().create(vals_list)
        return records

    def write(self, vals):
        """Backfill planned quantity after product/quote item change when empty."""
        if (
            len(self) > 1
            and ('quote_item_id' in vals or 'product_id' in vals)
            and 'planned_qty' not in vals
        ):
            return all(rec.write(vals) for rec in self)

        if (
            len(self) == 1
            and ('quote_item_id' in vals or 'product_id' in vals)
            and 'planned_qty' not in vals
        ):
            rec = self
            quote_item = self.env['btp.quote.item'].browse(vals['quote_item_id']) if vals.get('quote_item_id') else rec.quote_item_id
            product = self.env['product.product'].browse(vals['product_id']) if vals.get('product_id') else rec.product_id
            if quote_item and product and not rec.planned_qty:
                planned_qty = rec._get_quote_item_planned_qty(quote_item=quote_item, product=product)
                if planned_qty > 0:
                    vals = dict(vals)
                    vals['planned_qty'] = planned_qty
        return super().write(vals)

    def action_create_outbound_move(self):
        """Create an outbound stock move for this consumption (Module 9). Only for storable products."""
        self.ensure_one()
        if self.stock_move_id:
            raise ValidationError(_('A stock move is already linked to this consumption.'))
        # Odoo 19: storable = Track Inventory (is_storable), not type; type is consu/service/combo
        if not getattr(self.product_id.product_tmpl_id, 'is_storable', False):
            raise ValidationError(_('Outbound move can only be created for storable products. Enable "Track Inventory" on the product.'))
        company = self.site_id.company_id or self.env.company
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company.id)], limit=1)
        if not warehouse:
            raise ValidationError(_('No warehouse found for company %s.') % company.name)
        qty = self.real_qty or self.planned_qty
        if qty <= 0:
            raise ValidationError(_('Set a positive actual or planned quantity before creating the move.'))
        location_src = warehouse.lot_stock_id
        location_dest = self.env['stock.location'].search([
            ('company_id', '=', company.id),
            ('btp_site_id', '=', self.site_id.id),
        ], limit=1)
        if not location_dest:
            location_dest = company.scrap_location_id or warehouse.lot_stock_id
        picking_type = warehouse.out_type_id or self.env['stock.picking.type'].search([
            ('warehouse_id', '=', warehouse.id),
            ('code', '=', 'outgoing'),
        ], limit=1)
        move_vals = {
            'product_id': self.product_id.id,
            'product_uom_qty': qty,
            'product_uom': self.product_id.uom_id.id,
            'location_id': location_src.id,
            'location_dest_id': location_dest.id,
            'company_id': company.id,
            'origin': _('Site %s') % (self.site_id.btp_site_code or self.site_id.name),
            'btp_site_id': self.site_id.id,
            'btp_origin_type': 'site_consumption',
            'btp_consumption_id': self.id,
        }
        if picking_type:
            move_vals['picking_type_id'] = picking_type.id
        move = self.env['stock.move'].create(move_vals)
        move._action_confirm()
        self.stock_move_id = move.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'res_id': move.id,
            'view_mode': 'form',
            'target': 'current',
        }
