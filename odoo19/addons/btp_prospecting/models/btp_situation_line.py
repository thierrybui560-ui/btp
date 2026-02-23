# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.

from odoo import api, fields, models, _

class BtpSituationLine(models.Model):
    _name = 'btp.situation.line'
    _description = 'BTP Situation Line (Item Progress)'
    _order = 'situation_id, sequence, id'

    situation_id = fields.Many2one('btp.situation', string='Situation', required=True, ondelete='cascade', index=True)
    quote_item_id = fields.Many2one('btp.quote.item', string='Quote Item', ondelete='set null', index=True)
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Item', related='quote_item_id.name', readonly=True)
    total_amount = fields.Float(string='Global Item Amount', digits='Product Price')
    cumul_m = fields.Float(string='Cumulative at M', digits='Product Price', default=0.0)
    cumul_m_prev = fields.Float(string='Cumulative at M-1', digits='Product Price', default=0.0)
    month_progress = fields.Float(string="Month's Progress", digits='Product Price', compute='_compute_month_progress', store=True)
    balance_to_invoice = fields.Float(string='Balance to Invoice', digits='Product Price', compute='_compute_balance_to_invoice', store=True)

    @api.depends('cumul_m', 'cumul_m_prev')
    def _compute_month_progress(self):
        for line in self:
            line.month_progress = line.cumul_m - line.cumul_m_prev

    @api.depends('total_amount', 'cumul_m')
    def _compute_balance_to_invoice(self):
        for line in self:
            line.balance_to_invoice = line.total_amount - line.cumul_m
