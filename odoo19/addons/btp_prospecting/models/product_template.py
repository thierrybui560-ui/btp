# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    """Extend product.template for BTP Articles"""
    _inherit = 'product.template'

    # ========== BTP Article Identification ==========
    is_btp_article = fields.Boolean(
        string='Is BTP Article',
        default=False,
        help='This product is a BTP article (raw material, supply)'
    )
    btp_internal_reference = fields.Char(
        string='Internal Reference',
        index=True,
        help='Internal reference code for the article'
    )
    btp_designation = fields.Text(
        string='Designation',
        help='Full designation/description of the article'
    )

    # ========== Article Classification ==========
    btp_family_id = fields.Many2one(
        'btp.article.family',
        string='Family',
        ondelete='restrict',
        index=True,
        help='Article family (e.g., Flockings, Mortars)'
    )
    btp_subfamily_id = fields.Many2one(
        'btp.article.subfamily',
        string='Subfamily',
        ondelete='restrict',
        domain="[('family_id', '=', btp_family_id)]",
        index=True,
        help='Article subfamily (e.g., Fireproof, Acoustic)'
    )

    # ========== Pricing ==========
    btp_average_cost_price = fields.Float(
        string='Average Cost Price',
        digits='Product Price',
        compute='_compute_average_cost_price',
        store=True,
        help='Average purchase price from all suppliers'
    )
    btp_catalog_price = fields.Float(
        string='Catalog Price',
        digits='Product Price',
        help='Standard catalog price'
    )
    btp_last_purchase_price = fields.Float(
        string='Last Purchase Price',
        digits='Product Price',
        compute='_compute_last_purchase_price',
        store=True,
        help='Last purchase price from any supplier'
    )
    btp_last_purchase_date = fields.Date(
        string='Last Purchase Date',
        compute='_compute_last_purchase_price',
        store=True
    )
    btp_last_supplier_id = fields.Many2one(
        'res.partner',
        string='Last Supplier',
        compute='_compute_last_purchase_price',
        store=True,
        # Domain will be applied after module upgrade completes
    )

    # ========== Suppliers ==========
    btp_supplier_ids = fields.Many2many(
        'res.partner',
        'btp_article_supplier_rel',
        'article_id',
        'supplier_id',
        string='Suppliers',
        # Domain will be applied after module upgrade completes
        help='Suppliers that provide this article'
    )
    btp_supplier_count = fields.Integer(
        string='Suppliers Count',
        compute='_compute_supplier_count',
        store=True
    )

    # ========== Documents ==========
    btp_document_ids = fields.One2many(
        'btp.article.document',
        'article_id',
        string='Documents',
        help='Technical sheets, PV, SDS, notices'
    )
    btp_document_count = fields.Integer(
        string='Documents Count',
        compute='_compute_document_count',
        store=True
    )
    btp_expired_documents_count = fields.Integer(
        string='Expired Documents',
        compute='_compute_document_count',
        store=True
    )
    btp_expiring_soon_documents_count = fields.Integer(
        string='Expiring Soon Documents',
        compute='_compute_document_count',
        store=True
    )

    # ========== Price History ==========
    btp_price_history_ids = fields.One2many(
        'btp.article.price.history',
        'article_id',
        string='Price History',
        help='Purchase price history by supplier'
    )
    btp_price_history_count = fields.Integer(
        string='Price History Count',
        compute='_compute_price_history_count',
        store=True
    )

    @api.depends('btp_price_history_ids', 'btp_price_history_ids.purchase_price', 'btp_price_history_ids.quantity')
    def _compute_average_cost_price(self):
        for record in self:
            if record.btp_price_history_ids:
                total_cost = sum(
                    history.purchase_price * history.quantity
                    for history in record.btp_price_history_ids
                )
                total_qty = sum(history.quantity for history in record.btp_price_history_ids)
                record.btp_average_cost_price = total_cost / total_qty if total_qty > 0 else 0.0
            else:
                record.btp_average_cost_price = 0.0

    @api.depends('btp_price_history_ids')
    def _compute_last_purchase_price(self):
        for record in self:
            if record.btp_price_history_ids:
                last_history = record.btp_price_history_ids[0]  # Already ordered by date desc
                record.btp_last_purchase_price = last_history.purchase_price
                record.btp_last_purchase_date = last_history.purchase_date
                record.btp_last_supplier_id = last_history.supplier_id
            else:
                record.btp_last_purchase_price = 0.0
                record.btp_last_purchase_date = False
                record.btp_last_supplier_id = False

    @api.depends('btp_supplier_ids')
    def _compute_supplier_count(self):
        for record in self:
            record.btp_supplier_count = len(record.btp_supplier_ids)

    @api.depends('btp_document_ids', 'btp_document_ids.is_expired', 'btp_document_ids.expires_soon')
    def _compute_document_count(self):
        for record in self:
            record.btp_document_count = len(record.btp_document_ids)
            record.btp_expired_documents_count = len(record.btp_document_ids.filtered('is_expired'))
            record.btp_expiring_soon_documents_count = len(record.btp_document_ids.filtered('expires_soon'))

    @api.depends('btp_price_history_ids')
    def _compute_price_history_count(self):
        for record in self:
            record.btp_price_history_count = len(record.btp_price_history_ids)

    @api.onchange('btp_family_id')
    def _onchange_family_id(self):
        """Clear subfamily when family changes"""
        if self.btp_family_id:
            # Keep subfamily only if it belongs to the selected family
            if self.btp_subfamily_id and self.btp_subfamily_id.family_id != self.btp_family_id:
                self.btp_subfamily_id = False
        else:
            self.btp_subfamily_id = False

    @api.constrains('btp_subfamily_id', 'btp_family_id')
    def _check_subfamily_family(self):
        for record in self:
            if record.btp_subfamily_id and record.btp_family_id:
                if record.btp_subfamily_id.family_id != record.btp_family_id:
                    raise ValidationError(_('Subfamily must belong to the selected family.'))

