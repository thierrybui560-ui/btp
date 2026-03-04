# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 8 — Payments & Finances: Cash forecast (inflows/outflows by period).

from datetime import timedelta
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BtpCashForecastLine(models.TransientModel):
    _name = 'btp.cash.forecast.line'
    _description = 'BTP Cash Forecast Line (computed)'

    date = fields.Date(string='Date', required=True)
    period_label = fields.Char(string='Period', help='Week, month or quarter label')
    amount_in = fields.Float(string='Inflows', digits='Product Price', default=0.0)
    amount_out = fields.Float(string='Outflows', digits='Product Price', default=0.0)
    balance = fields.Float(string='Balance', digits='Product Price', default=0.0)
    cumulative_balance = fields.Float(string='Cumulative', digits='Product Price', default=0.0)
    project_id = fields.Many2one('project.project', string='Site', ondelete='set null')
    company_id = fields.Many2one('res.company', string='Company', ondelete='set null')
    forecast_id = fields.Many2one('btp.cash.forecast', string='Forecast', ondelete='cascade')


class BtpCashForecast(models.TransientModel):
    _name = 'btp.cash.forecast'
    _description = 'BTP Cash Forecast (wizard result)'

    date_from = fields.Date(string='From', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='To', required=True)
    group_by = fields.Selection([
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('quarter', 'Quarter'),
    ], string='Group By', default='month', required=True)
    project_id = fields.Many2one('project.project', string='Site', help='Leave empty for all sites')
    company_id = fields.Many2one('res.company', string='Company', help='Leave empty for all companies')
    line_ids = fields.One2many(
        'btp.cash.forecast.line',
        'forecast_id',
        string='Lines',
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        from dateutil.relativedelta import relativedelta
        today = fields.Date.context_today(self)
        if not res.get('date_to'):
            res['date_to'] = today + relativedelta(months=3)
        return res

    def _period_key(self, date):
        if self.group_by == 'day':
            return date, date.strftime('%Y-%m-%d')
        if self.group_by == 'week':
            start = date - timedelta(days=date.weekday())
            return start, _('W%02d %s') % (date.isocalendar()[1], str(start)[:7])
        if self.group_by == 'month':
            start = date.replace(day=1)
            return start, date.strftime('%Y-%m')
        if self.group_by == 'quarter':
            q = (date.month - 1) // 3 + 1
            start = date.replace(month=(q - 1) * 3 + 1, day=1)
            return start, _('Q%s %s') % (q, date.year)
        return date, str(date)

    def action_compute(self):
        self.ensure_one()
        if self.date_to < self.date_from:
            raise UserError(_('End date must be after start date.'))
        Move = self.env['account.move']
        domain_in = [
            ('move_type', '=', 'out_invoice'),
            ('state', 'in', ('posted', 'draft')),
            ('invoice_date_due', '>=', self.date_from),
            ('invoice_date_due', '<=', self.date_to),
        ]
        domain_out = [
            ('move_type', '=', 'in_invoice'),
            ('state', 'in', ('posted', 'draft')),
            ('invoice_date_due', '>=', self.date_from),
            ('invoice_date_due', '<=', self.date_to),
        ]
        if self.project_id:
            domain_in.append(('btp_site_id', '=', self.project_id.id))
            domain_out.append(('btp_site_id', '=', self.project_id.id))
        if self.company_id:
            domain_in.append(('company_id', '=', self.company_id.id))
            domain_out.append(('company_id', '=', self.company_id.id))

        inflows = defaultdict(lambda: {'amount': 0.0, 'company_id': False, 'project_id': False})
        outflows = defaultdict(lambda: {'amount': 0.0, 'company_id': False, 'project_id': False})

        for move in Move.search(domain_in):
            due = move.invoice_date_due or move.invoice_date
            if not due:
                continue
            period_date, period_label = self._period_key(due)
            key = (period_date, move.company_id.id, move.btp_site_id.id if move.btp_site_id else 0)
            amount = move.amount_total_signed or 0.0
            if amount > 0:
                inflows[key]['amount'] += amount
                inflows[key]['company_id'] = move.company_id.id
                inflows[key]['project_id'] = move.btp_site_id.id if move.btp_site_id else False

        for move in Move.search(domain_out):
            due = move.invoice_date_due or move.invoice_date
            if not due:
                continue
            period_date, period_label = self._period_key(due)
            key = (period_date, move.company_id.id, move.btp_site_id.id if move.btp_site_id else 0)
            amount = abs(move.amount_total_signed or 0.0)
            outflows[key]['amount'] += amount
            outflows[key]['company_id'] = move.company_id.id
            outflows[key]['project_id'] = move.btp_site_id.id if move.btp_site_id else False

        all_keys = set(inflows.keys()) | set(outflows.keys())
        lines = []
        for (period_date, company_id, project_id) in sorted(all_keys):
            in_val = inflows[(period_date, company_id, project_id)]['amount']
            out_val = outflows[(period_date, company_id, project_id)]['amount']
            _, period_label = self._period_key(period_date)
            lines.append((0, 0, {
                'date': period_date,
                'period_label': period_label,
                'amount_in': in_val,
                'amount_out': out_val,
                'balance': in_val - out_val,
                'company_id': company_id or False,
                'project_id': project_id or False,
            }))
        lines.sort(key=lambda x: (x[2]['date'], x[2].get('company_id') or 0, x[2].get('project_id') or 0))
        cumul = 0.0
        for line_vals in lines:
            line_vals[2]['cumulative_balance'] = cumul + line_vals[2]['balance']
            cumul = line_vals[2]['cumulative_balance']
        self.write({'line_ids': [(5, 0, 0)] + lines})
        return self._action_open_lines()

    def _action_open_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'btp.cash.forecast.line',
            'name': _('Cash Forecast'),
            'view_mode': 'graph,pivot,list',
            'domain': [('forecast_id', '=', self.id)],
            'context': {'create': False, 'edit': False},
        }
