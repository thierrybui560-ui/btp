# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class BtpArticleFamily(models.Model):
    """Article Family - Top level category for articles"""
    _name = 'btp.article.family'
    _description = 'Article Family'
    _order = 'sequence, name'

    name = fields.Char(
        string='Family Name',
        required=True,
        index=True,
        help='Name of the article family (e.g., Flockings, Mortars)'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display'
    )
    subfamily_ids = fields.One2many(
        'btp.article.subfamily',
        'family_id',
        string='Subfamilies'
    )
    subfamily_count = fields.Integer(
        string='Subfamilies Count',
        compute='_compute_subfamily_count',
        store=True
    )
    article_count = fields.Integer(
        string='Articles Count',
        compute='_compute_article_count',
        store=True
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    description = fields.Text(
        string='Description',
        help='Description of the article family'
    )

    @api.depends('subfamily_ids')
    def _compute_subfamily_count(self):
        for record in self:
            record.subfamily_count = len(record.subfamily_ids)

    @api.depends('subfamily_ids', 'subfamily_ids.article_count')
    def _compute_article_count(self):
        for record in self:
            record.article_count = sum(record.subfamily_ids.mapped('article_count'))


class BtpArticleSubfamily(models.Model):
    """Article Subfamily - Second level category for articles"""
    _name = 'btp.article.subfamily'
    _description = 'Article Subfamily'
    _order = 'family_id, sequence, name'

    name = fields.Char(
        string='Subfamily Name',
        required=True,
        index=True,
        help='Name of the article subfamily (e.g., Fireproof, Acoustic)'
    )
    family_id = fields.Many2one(
        'btp.article.family',
        string='Family',
        required=True,
        ondelete='cascade',
        index=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display within the family'
    )
    article_count = fields.Integer(
        string='Articles Count',
        compute='_compute_article_count',
        store=True
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    description = fields.Text(
        string='Description',
        help='Description of the article subfamily'
    )

    @api.depends('family_id')
    def _compute_article_count(self):
        for record in self:
            # Count articles in this subfamily
            articles = self.env['product.template'].search([
                ('btp_subfamily_id', '=', record.id),
                ('is_btp_article', '=', True)
            ])
            record.article_count = len(articles)

