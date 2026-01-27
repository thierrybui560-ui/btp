# -*- coding: utf-8 -*-

from odoo import models, fields, tools


class BtpArticlePriceStats(models.Model):
    _name = 'btp.article.price.stats'
    _description = 'Article Price Stats'
    _auto = False
    _order = 'month desc, article_id'

    article_id = fields.Many2one('product.template', string='Article', readonly=True)
    supplier_id = fields.Many2one('res.partner', string='Supplier', readonly=True)
    month = fields.Date(string='Month', readonly=True)
    avg_price = fields.Float(string='Average Price', readonly=True, digits='Product Price')
    min_price = fields.Float(string='Min Price', readonly=True, digits='Product Price')
    max_price = fields.Float(string='Max Price', readonly=True, digits='Product Price')
    purchase_count = fields.Integer(string='Purchases', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER () AS id,
                    article_id,
                    supplier_id,
                    date_trunc('month', purchase_date)::date AS month,
                    AVG(purchase_price) AS avg_price,
                    MIN(purchase_price) AS min_price,
                    MAX(purchase_price) AS max_price,
                    COUNT(*) AS purchase_count
                FROM btp_article_price_history
                GROUP BY article_id, supplier_id, date_trunc('month', purchase_date)
            )
        """ % self._table)

