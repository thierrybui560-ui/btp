# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class BtpQuoteLot(models.Model):
    """Quote Lot - Top level in quote hierarchy"""
    _name = 'btp.quote.lot'
    _description = 'Quote Lot'
    _order = 'quote_id, sequence, name'

    name = fields.Char(
        string='Lot Name',
        required=True,
        help='Name of the lot (e.g., Fireproof flocking, Acoustic insulation)'
    )
    quote_id = fields.Many2one(
        'sale.order',
        string='Quote',
        required=True,
        ondelete='cascade',
        index=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display'
    )
    title_ids = fields.One2many(
        'btp.quote.title',
        'lot_id',
        string='Titles'
    )
    title_count = fields.Integer(
        string='Titles Count',
        compute='_compute_title_count',
        store=True
    )
    description = fields.Text(
        string='Description',
        help='Description of the lot'
    )

    @api.depends('title_ids')
    def _compute_title_count(self):
        for record in self:
            record.title_count = len(record.title_ids)


class BtpQuoteTitle(models.Model):
    """Quote Title - Second level in quote hierarchy"""
    _name = 'btp.quote.title'
    _description = 'Quote Title'
    _order = 'lot_id, sequence, name'

    name = fields.Char(
        string='Title Name',
        required=True,
        help='Name of the title (e.g., Wall flocking, Floor flocking)'
    )
    lot_id = fields.Many2one(
        'btp.quote.lot',
        string='Lot',
        required=True,
        ondelete='cascade',
        index=True
    )
    quote_id = fields.Many2one(
        'sale.order',
        string='Quote',
        related='lot_id.quote_id',
        store=True,
        readonly=True,
        index=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display within the lot'
    )
    subtitle_ids = fields.One2many(
        'btp.quote.subtitle',
        'title_id',
        string='Subtitles'
    )
    subtitle_count = fields.Integer(
        string='Subtitles Count',
        compute='_compute_subtitle_count',
        store=True
    )
    description = fields.Text(
        string='Description',
        help='Description of the title'
    )

    @api.depends('subtitle_ids')
    def _compute_subtitle_count(self):
        for record in self:
            record.subtitle_count = len(record.subtitle_ids)


class BtpQuoteSubtitle(models.Model):
    """Quote Subtitle - Third level in quote hierarchy"""
    _name = 'btp.quote.subtitle'
    _description = 'Quote Subtitle'
    _order = 'title_id, sequence, name'

    name = fields.Char(
        string='Subtitle Name',
        required=True,
        help='Name of the subtitle (e.g., Concrete flocking, Metal flocking)'
    )
    title_id = fields.Many2one(
        'btp.quote.title',
        string='Title',
        required=True,
        ondelete='cascade',
        index=True
    )
    lot_id = fields.Many2one(
        'btp.quote.lot',
        string='Lot',
        related='title_id.lot_id',
        store=True,
        readonly=True,
        index=True
    )
    quote_id = fields.Many2one(
        'sale.order',
        string='Quote',
        related='title_id.quote_id',
        store=True,
        readonly=True,
        index=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display within the title'
    )
    item_ids = fields.One2many(
        'btp.quote.item',
        'subtitle_id',
        string='Items'
    )
    item_count = fields.Integer(
        string='Items Count',
        compute='_compute_item_count',
        store=True
    )
    description = fields.Text(
        string='Description',
        help='Description of the subtitle'
    )

    @api.depends('item_ids')
    def _compute_item_count(self):
        for record in self:
            record.item_count = len(record.item_ids)

