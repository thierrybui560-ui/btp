# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 11 — Reports & Exports

import logging
from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

REPORT_SCOPE = [
    ('commercial_leads_quotes', 'Leads & Quotes by Salesperson'),
    ('lot_cost_consumption', 'Costs & Consumption by Quote Lot'),
    ('site_progress', 'Site Progress, Costs & Margins'),
    ('client_volume', 'Business Volume by Client'),
    ('salesperson_activity', 'Salesperson Activity (leads, quotes, conversion)'),
    ('employee_productivity', 'Employee Productivity (hours, pointing, sites)'),
    ('team_performance', 'Team Performance (yield, assigned sites)'),
    ('article_consumption', 'Article Consumption (planned vs actual)'),
    ('article_rotation', 'Article Rotation & Stock Movements'),
    ('supplier_analysis', 'Supplier / Price Analysis'),
    ('qhse_incidents', 'QHSE Incidents by Site'),
    ('combined_geo_commercial', 'Commercial Performance by Geographic Area'),
    ('combined_article_site_supplier', 'Article Consumption by Site & Supplier'),
    ('combined_margin_salesperson_client', 'Net Margin by Salesperson & Client'),
    ('margin_consumption_combined', 'Net Margin & Article Consumption'),
    # Module 13 — Multi-companies consolidation
    ('consolidated_turnover', 'Consolidated Turnover by Company'),
    ('consolidated_cash', 'Consolidated Cash / Invoiced by Company'),
    ('consolidated_margin', 'Consolidated Net Margin by Company & Site'),
    ('shared_clients_distribution', 'Shared Clients Distribution'),
    # Module 15 — System Governance
    ('data_quality', 'Data Quality (duplicates, documentary conformity)'),
    ('governance_reattributions', 'Governance: Reattributions'),
]

OUTPUT_FORMAT = [
    ('pdf', 'PDF'),
    ('xlsx', 'Excel'),
    ('csv', 'CSV'),
]

SCHEDULE = [
    ('none', 'Manual only'),
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
]


class BtpReportTemplate(models.Model):
    _name = 'btp.report.template'
    _description = 'BTP Report Template'
    _order = 'name'

    name = fields.Char(string='Report Name', required=True)
    scope = fields.Selection(
        REPORT_SCOPE,
        string='Scope',
        required=True,
        help='Type of data included in the report.',
    )
    date_from = fields.Date(string='From Date', help='Optional period filter (leave empty for all).')
    date_to = fields.Date(string='To Date', help='Optional period filter (leave empty for all).')
    geographic_area = fields.Char(
        string='Geographic Area',
        help='Optional city/zip/country filter for geo-oriented scopes.',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help='Restrict to one company (leave empty for all).',
    )
    output_format = fields.Selection(
        OUTPUT_FORMAT,
        string='Output Format',
        default='pdf',
        required=True,
    )
    schedule = fields.Selection(
        SCHEDULE,
        string='Schedule',
        default='none',
        help='Automated run frequency; Manual only = run on demand.',
    )
    recipient_user_ids = fields.Many2many(
        'res.users',
        'btp_report_template_user_rel',
        'template_id',
        'user_id',
        string='Email Recipients',
        help='Users who receive the report by email when run (including scheduled).',
    )
    active = fields.Boolean(default=True)
    export_job_ids = fields.One2many(
        'btp.export.job',
        'report_template_id',
        string='Export History',
        copy=False,
    )
    export_job_count = fields.Integer(
        string='Exports',
        compute='_compute_export_job_count',
        store=False,
    )

    @api.depends('export_job_ids')
    def _compute_export_job_count(self):
        for r in self:
            r.export_job_count = len(r.export_job_ids)

    @api.model_create_multi
    def create(self, vals_list):
        consolidation_scopes = {
            'consolidated_turnover',
            'consolidated_cash',
            'consolidated_margin',
            'shared_clients_distribution',
        }
        for vals in vals_list:
            if vals.get('scope') in consolidation_scopes and 'company_id' not in vals:
                vals['company_id'] = False
        records = super().create(vals_list)
        for rec in records:
            self.env['btp.audit.log'].sudo().log(
                'create',
                model_name=rec._name,
                res_id=rec.id,
                reason=_('Report template created: %s') % rec.name,
                company_id=rec.company_id.id if rec.company_id else self.env.company.id,
            )
        return records

    @api.onchange('scope')
    def _onchange_scope_company_for_consolidation(self):
        if self.scope in {
            'consolidated_turnover',
            'consolidated_cash',
            'consolidated_margin',
            'shared_clients_distribution',
        }:
            self.company_id = False

    def write(self, vals):
        result = super().write(vals)
        for rec in self:
            self.env['btp.audit.log'].sudo().log(
                'write',
                model_name=rec._name,
                res_id=rec.id,
                reason=_('Report template updated: %s') % rec.name,
                company_id=rec.company_id.id if rec.company_id else self.env.company.id,
            )
        return result

    def unlink(self):
        logs = [(rec.id, rec.name, rec.company_id.id if rec.company_id else self.env.company.id) for rec in self]
        result = super().unlink()
        for rec_id, rec_name, company_id in logs:
            self.env['btp.audit.log'].sudo().log(
                'unlink',
                model_name=self._name,
                res_id=rec_id,
                reason=_('Report template deleted: %s') % rec_name,
                company_id=company_id,
            )
        return result

    def action_run_report(self):
        """Generate report now and optionally send by email."""
        self.ensure_one()
        return self._generate_and_store(send_email=True)

    def action_run_report_no_email(self):
        """Generate report now without sending email."""
        self.ensure_one()
        return self._generate_and_store(send_email=False)

    def action_open_export_jobs(self):
        """Open export history for this template."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'btp.export.job',
            'name': _('Export History'),
            'view_mode': 'list,form',
            'domain': [('report_template_id', '=', self.id)],
        }

    @api.model
    def _cron_run_scheduled_reports(self):
        """Run templates that are due (daily / weekly / monthly).
        Weekly runs on Monday or if no export in the last 8 days (e.g. first run / manual trigger).
        Monthly runs on the 1st or if no export in the last 31 days (e.g. first run / manual trigger).
        """
        today = fields.Date.today()
        weekday = today.weekday()  # 0 = Monday
        day_of_month = today.day
        domain = [
            ('active', '=', True),
            ('schedule', '!=', 'none'),
        ]
        templates = self.search(domain)
        for t in templates:
            due = False
            if t.schedule == 'daily':
                due = True
            elif t.schedule == 'weekly':
                # Due on Monday or if no export in last 8 days (first run or manual cron test)
                cutoff_weekly = today - timedelta(days=8)
                has_recent = self.env['btp.export.job'].search_count([
                    ('report_template_id', '=', t.id),
                    ('run_date', '>=', cutoff_weekly),
                ]) > 0
                due = (weekday == 0) or not has_recent
            elif t.schedule == 'monthly':
                # Due on 1st or if no export in last 31 days (first run or manual cron test)
                cutoff_monthly = today - timedelta(days=31)
                has_recent = self.env['btp.export.job'].search_count([
                    ('report_template_id', '=', t.id),
                    ('run_date', '>=', cutoff_monthly),
                ]) > 0
                due = (day_of_month == 1) or not has_recent
            if not due:
                continue
            try:
                t._generate_and_store(send_email=True)
                _logger.info('BTP scheduled report "%s" generated and sent.', t.name)
            except Exception as e:
                _logger.exception('BTP scheduled report "%s" failed: %s', t.name, e)

    def _generate_and_store(self, send_email=False):
        """Generate report file, create export job, optionally email recipients."""
        self.ensure_one()
        job = self.env['btp.export.job'].create({
            'report_template_id': self.id,
            'state': 'pending',
        })
        try:
            content, filename, mimetype = self._generate_report_content()
            if not content:
                raise UserError(_('Report generated no data.'))
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'datas': content,
                'res_model': 'btp.export.job',
                'res_id': job.id,
                'type': 'binary',
                'mimetype': mimetype,
            })
            job.write({
                'state': 'done',
                'attachment_id': attachment.id,
            })
            if send_email and self.recipient_user_ids:
                job._send_report_email(attachment)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'btp.export.job',
                'res_id': job.id,
                'view_mode': 'form',
                'target': 'current',
            }
        except Exception as e:
            job.write({
                'state': 'failed',
                'error_message': str(e),
            })
            raise UserError(_('Report generation failed: %s') % e)

    def _generate_report_content(self):
        """Return (base64_content, filename, mimetype)."""
        data = self._get_report_data()
        if self.output_format == 'pdf':
            return self._render_pdf(data)
        if self.output_format == 'xlsx':
            return self._render_xlsx(data)
        if self.output_format == 'csv':
            return self._render_csv(data)
        raise UserError(_('Unknown format %s') % self.output_format)

    def _get_report_data(self):
        """Return dict with keys: title, headers, rows, and optional extra for PDF."""
        scope_method = '_get_data_%s' % self.scope
        if not hasattr(self, scope_method):
            raise UserError(_('Report scope "%s" is not implemented.') % self.scope)
        return getattr(self, scope_method)()

    def _get_data_commercial_leads_quotes(self):
        """Leads and quotes by salesperson."""
        domain = [('btp_quote_number', '!=', False)]
        if self.date_from:
            domain.append(('date_order', '>=', self.date_from))
        if self.date_to:
            domain.append(('date_order', '<=', self.date_to))
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        if self.geographic_area:
            ga = self.geographic_area.strip()
            domain += ['|', '|',
                       ('partner_shipping_id.city', 'ilike', ga),
                       ('partner_shipping_id.zip', 'ilike', ga),
                       ('partner_shipping_id.country_id.name', 'ilike', ga)]
        orders = self.env['sale.order'].search(domain, order='user_id, date_order')
        # Aggregate by user
        by_user = {}
        for o in orders:
            u = o.user_id
            key = (u.id, u.name if u else _('No salesperson'))
            if key not in by_user:
                by_user[key] = {'user': key[1], 'quotes': 0, 'total': 0.0, 'converted': 0}
            by_user[key]['quotes'] += 1
            by_user[key]['total'] += o.amount_total or 0
            if o.state in ('sale', 'done'):
                by_user[key]['converted'] += 1
        lead_domain = [('converted', '=', True)]
        if self.date_from:
            lead_domain.append(('write_date', '>=', self.date_from))
        if self.date_to:
            lead_domain.append(('write_date', '<=', self.date_to))
        if self.company_id:
            lead_domain.append(('company_id', '=', self.company_id.id))
        leads = self.env['btp.lead'].search(lead_domain)
        lead_by_user = {}
        for l in leads:
            u = l.user_id
            key = (u.id if u else 0, u.name if u else _('No salesperson'))
            lead_by_user[key] = lead_by_user.get(key, 0) + 1
        headers = [_('Salesperson'), _('Quotes'), _('Converted'), _('Total amount'), _('Leads converted')]
        rows = []
        for (uid, name), v in sorted(by_user.items(), key=lambda x: x[0][1] or ''):
            rows.append([
                name,
                v['quotes'],
                v['converted'],
                '%.2f' % v['total'],
                lead_by_user.get((uid, name), 0),
            ])
        if not rows:
            rows = [[_('No data for the selected period.')]]
        return {'title': _('Leads & Quotes by Salesperson'), 'headers': headers, 'rows': rows}

    def _get_data_site_progress(self):
        """Site progress, costs, margins."""
        domain = [('btp_site_code', '!=', False)]
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        if self.geographic_area:
            ga = self.geographic_area.strip()
            domain += ['|', '|',
                       ('btp_site_city', 'ilike', ga),
                       ('btp_site_zip', 'ilike', ga),
                       ('btp_site_country_id.name', 'ilike', ga)]
        sites = self.env['project.project'].search(domain, order='btp_site_code')
        headers = [
            _('Site Code'), _('Site Name'), _('Quote Total'), _('Invoiced'), _('Actual Costs'),
            _('Net Margin'), _('Margin %'), _('QHSE Incidents'),
        ]
        rows = []
        for s in sites:
            incidents = self.env['btp.qse.incident'].search_count([('site_id', '=', s.id)])
            rows.append([
                s.btp_site_code or '',
                s.name or '',
                '%.2f' % (s.btp_quote_total or 0),
                '%.2f' % (s.btp_invoiced_total or 0),
                '%.2f' % (s.btp_actual_costs or 0),
                '%.2f' % (s.btp_net_margin or 0),
                '%.1f' % (s.btp_margin_percent or 0),
                incidents,
            ])
        if not rows:
            rows = [[_('No sites.')]]
        return {'title': _('Site Progress, Costs & Margins'), 'headers': headers, 'rows': rows}

    def _get_data_client_volume(self):
        """Business volume by client (from sale orders)."""
        domain = []
        if self.date_from:
            domain.append(('date_order', '>=', self.date_from))
        if self.date_to:
            domain.append(('date_order', '<=', self.date_to))
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        if self.geographic_area:
            ga = self.geographic_area.strip()
            domain += ['|', '|',
                       ('partner_id.city', 'ilike', ga),
                       ('partner_id.zip', 'ilike', ga),
                       ('partner_id.country_id.name', 'ilike', ga)]
        orders = self.env['sale.order'].search(domain, order='partner_id')
        by_partner = {}
        for o in orders:
            p = o.partner_id
            key = (p.id, p.name if p else _('No client'))
            if key not in by_partner:
                by_partner[key] = {'name': key[1], 'quotes': 0, 'orders': 0, 'total': 0.0}
            if o.btp_quote_number:
                by_partner[key]['quotes'] += 1
            if o.state in ('sale', 'done'):
                by_partner[key]['orders'] += 1
            by_partner[key]['total'] += o.amount_total or 0
        headers = [_('Client'), _('Quotes'), _('Orders'), _('Conversion %'), _('Total amount')]
        rows = []
        for _key, v in sorted(by_partner.items(), key=lambda x: x[1]['name']):
            conv = (v['orders'] / v['quotes'] * 100.0) if v['quotes'] else 0.0
            rows.append([v['name'], v['quotes'], v['orders'], '%.1f' % conv, '%.2f' % v['total']])
        if not rows:
            rows = [[_('No data.')]]
        return {'title': _('Business Volume by Client'), 'headers': headers, 'rows': rows}

    def _get_data_salesperson_activity(self):
        """Salesperson: leads processed, quotes, success rate."""
        domain = []
        if self.date_from:
            domain.append(('create_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('create_date', '<=', self.date_to))
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        leads = self.env['btp.lead'].search(domain)
        by_user = {}
        for l in leads:
            u = l.user_id
            key = (u.id if u else 0, u.name if u else _('No user'))
            if key not in by_user:
                by_user[key] = {'name': key[1], 'leads': 0, 'converted': 0, 'quotes_won': 0}
            by_user[key]['leads'] += 1
            if l.converted:
                by_user[key]['converted'] += 1
        order_domain = [
            ('btp_quote_number', '!=', False),
            ('state', 'in', ('sale', 'done')),
        ]
        if self.date_from:
            order_domain.append(('date_order', '>=', self.date_from))
        if self.date_to:
            order_domain.append(('date_order', '<=', self.date_to))
        if self.company_id:
            order_domain.append(('company_id', '=', self.company_id.id))
        orders = self.env['sale.order'].search(order_domain)
        for o in orders:
            u = o.user_id
            key = (u.id if u else 0, u.name if u else _('No user'))
            if key not in by_user:
                by_user[key] = {'name': key[1], 'leads': 0, 'converted': 0, 'quotes_won': 0}
            by_user[key]['quotes_won'] = by_user[key].get('quotes_won', 0) + 1
        headers = [_('Salesperson'), _('Leads'), _('Converted'), _('Quotes won'), _('Conversion %')]
        rows = []
        for (_uid, name), v in sorted(by_user.items(), key=lambda x: x[0][1] or ''):
            quotes_won = v.get('quotes_won', 0)
            conv = (v['converted'] / v['leads'] * 100) if v['leads'] else 0
            rows.append([name, v['leads'], v['converted'], quotes_won, '%.1f' % conv])
        if not rows:
            rows = [[_('No data.')]]
        return {'title': _('Salesperson Activity'), 'headers': headers, 'rows': rows}

    def _get_data_article_consumption(self):
        """Article consumption: planned vs actual by site/article."""
        domain = []
        if self.company_id:
            domain.append(('site_id.company_id', '=', self.company_id.id))
        consumptions = self.env['btp.site.consumption'].search(domain, order='site_id, product_id')
        headers = [_('Site'), _('Article'), _('Planned'), _('Actual'), _('Variance'), _('Overconsumption')]
        rows = []
        for c in consumptions:
            var = (c.real_qty or 0) - (c.planned_qty or 0)
            rows.append([
                c.site_id.name or '',
                c.product_id.name if c.product_id else '',
                '%.2f' % (c.planned_qty or 0),
                '%.2f' % (c.real_qty or 0),
                '%.2f' % var,
                _('Yes') if c.overconsumption_alert else _('No'),
            ])
        if not rows:
            rows = [[_('No consumptions.')]]
        return {'title': _('Article Consumption'), 'headers': headers, 'rows': rows}

    def _get_data_supplier_analysis(self):
        """Supplier / price analysis from price history."""
        domain = []
        if self.date_from:
            domain.append(('purchase_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('purchase_date', '<=', self.date_to))
        history = self.env['btp.article.price.history'].search(domain, order='supplier_id, article_id')
        headers = [_('Supplier'), _('Article'), _('Lines'), _('Average price'), _('Purchased qty'), _('Conformity')]
        grouped = {}
        for h in history:
            key = (h.supplier_id.id if h.supplier_id else 0, h.article_id.id if h.article_id else 0)
            if key not in grouped:
                grouped[key] = {
                    'supplier': h.supplier_id.name if h.supplier_id else '',
                    'article': h.article_id.name if h.article_id else '',
                    'lines': 0,
                    'qty': 0.0,
                    'amount': 0.0,
                    'conformity': h.supplier_id.btp_conformity_status if h.supplier_id else '',
                }
            grouped[key]['lines'] += 1
            grouped[key]['qty'] += (h.quantity or 0.0)
            grouped[key]['amount'] += (h.purchase_price or 0.0) * (h.quantity or 0.0)
        rows = []
        for _key, g in sorted(grouped.items(), key=lambda x: (x[1]['supplier'], x[1]['article'])):
            avg = (g['amount'] / g['qty']) if g['qty'] else 0.0
            rows.append([
                g['supplier'],
                g['article'],
                g['lines'],
                '%.2f' % avg,
                '%.2f' % g['qty'],
                g['conformity'] or '',
            ])
        if not rows:
            rows = [[_('No price history.')]]
        return {'title': _('Supplier / Price Analysis'), 'headers': headers, 'rows': rows}

    def _get_data_lot_cost_consumption(self):
        """Costs and consumptions by quote lot."""
        domain = []
        if self.date_from:
            domain.append(('quote_id.date_order', '>=', self.date_from))
        if self.date_to:
            domain.append(('quote_id.date_order', '<=', self.date_to))
        if self.company_id:
            domain.append(('quote_id.company_id', '=', self.company_id.id))
        lots = self.env['btp.quote.lot'].search(domain, order='quote_id, sequence')
        headers = [_('Quote'), _('Lot'), _('Items'), _('Subtotal'), _('Total Cost'), _('Margin'), _('Margin %')]
        rows = []
        Item = self.env['btp.quote.item']
        for lot in lots:
            items = Item.search([('lot_id', '=', lot.id)])
            subtotal = sum(items.mapped('subtotal'))
            total_cost = sum(items.mapped('total_cost'))
            margin = subtotal - total_cost
            margin_pct = (margin / subtotal * 100.0) if subtotal else 0.0
            rows.append([
                lot.quote_id.name or '',
                lot.name or '',
                len(items),
                '%.2f' % subtotal,
                '%.2f' % total_cost,
                '%.2f' % margin,
                '%.1f' % margin_pct,
            ])
        if not rows:
            rows = [[_('No quote lots.')]]
        return {'title': _('Costs & Consumption by Quote Lot'), 'headers': headers, 'rows': rows}

    def _get_data_employee_productivity(self):
        """Employee productivity from pointing entries."""
        domain = [('user_id', '!=', False)]
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        if self.company_id:
            domain.append(('site_id.company_id', '=', self.company_id.id))
        pointings = self.env['btp.site.pointing'].search(domain, order='user_id, date')
        by_user = {}
        for p in pointings:
            key = p.user_id.id
            if key not in by_user:
                by_user[key] = {
                    'employee': p.user_id.name,
                    'hours': 0.0,
                    'qty': 0.0,
                    'sites': set(),
                    'entries': 0,
                }
            by_user[key]['hours'] += (p.hours or 0.0)
            by_user[key]['qty'] += (p.qty_done or 0.0)
            by_user[key]['entries'] += 1
            if p.site_id:
                by_user[key]['sites'].add(p.site_id.id)
        headers = [_('Employee'), _('Pointing entries'), _('Hours'), _('Qty done'), _('Sites followed')]
        rows = []
        for _key, v in sorted(by_user.items(), key=lambda x: x[1]['employee']):
            rows.append([
                v['employee'],
                v['entries'],
                '%.2f' % v['hours'],
                '%.2f' % v['qty'],
                len(v['sites']),
            ])
        if not rows:
            rows = [[_('No pointing entries.')]]
        return {'title': _('Employee Productivity'), 'headers': headers, 'rows': rows}

    def _get_data_team_performance(self):
        """Team performance: average yields and assigned sites."""
        lead_domain = []
        if self.date_from:
            lead_domain.append(('create_date', '>=', self.date_from))
        if self.date_to:
            lead_domain.append(('create_date', '<=', self.date_to))
        if self.company_id:
            lead_domain.append(('company_id', '=', self.company_id.id))
        leads = self.env['btp.lead'].search(lead_domain)
        perf_domain = []
        if self.date_from:
            perf_domain.append(('date', '>=', self.date_from))
        if self.date_to:
            perf_domain.append(('date', '<=', self.date_to))
        if self.company_id:
            perf_domain.append(('project_id.company_id', '=', self.company_id.id))
        perfs = self.env['btp.site.performance'].search(perf_domain)
        by_team = {}
        for l in leads:
            team = l.user_id.sale_team_id
            if not team:
                continue
            tid = team.id
            if tid not in by_team:
                by_team[tid] = {'team': team.name, 'leads': 0, 'sites': set(), 'yield_sum': 0.0, 'yield_n': 0}
            by_team[tid]['leads'] += 1
        for p in perfs:
            team = p.project_id.user_id.sale_team_id
            if not team:
                continue
            tid = team.id
            if tid not in by_team:
                by_team[tid] = {'team': team.name, 'leads': 0, 'sites': set(), 'yield_sum': 0.0, 'yield_n': 0}
            by_team[tid]['yield_sum'] += (p.performance_rate or 0.0)
            by_team[tid]['yield_n'] += 1
            if p.project_id:
                by_team[tid]['sites'].add(p.project_id.id)
        headers = [_('Team'), _('Processed leads'), _('Assigned sites'), _('Average yield %')]
        rows = []
        for _key, v in sorted(by_team.items(), key=lambda x: x[1]['team']):
            avg_yield = (v['yield_sum'] / v['yield_n']) if v['yield_n'] else 0.0
            rows.append([v['team'], v['leads'], len(v['sites']), '%.1f' % avg_yield])
        if not rows:
            rows = [[_('No team data.')]]
        return {'title': _('Team Performance'), 'headers': headers, 'rows': rows}

    def _get_data_article_rotation(self):
        """Article stock rotations and movement totals."""
        domain = [('state', '=', 'done'), ('product_id', '!=', False)]
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        moves = self.env['stock.move'].search(domain, order='product_id')
        grouped = {}
        for m in moves:
            key = m.product_id.id
            if key not in grouped:
                grouped[key] = {
                    'article': m.product_id.display_name,
                    'moves': 0,
                    'qty': 0.0,
                    'sites': set(),
                }
            grouped[key]['moves'] += 1
            grouped[key]['qty'] += (m.quantity or 0.0)
            if m.btp_site_id:
                grouped[key]['sites'].add(m.btp_site_id.id)
        headers = [_('Article'), _('Stock moves'), _('Moved quantity'), _('Sites touched')]
        rows = []
        for _key, g in sorted(grouped.items(), key=lambda x: x[1]['article']):
            rows.append([g['article'], g['moves'], '%.2f' % g['qty'], len(g['sites'])])
        if not rows:
            rows = [[_('No stock moves.')]]
        return {'title': _('Article Rotation & Stock Movements'), 'headers': headers, 'rows': rows}

    def _get_data_combined_geo_commercial(self):
        """Commercial performance by geographic area (city/zip/country)."""
        domain = []
        if self.date_from:
            domain.append(('date_order', '>=', self.date_from))
        if self.date_to:
            domain.append(('date_order', '<=', self.date_to))
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        if self.geographic_area:
            ga = self.geographic_area.strip()
            domain += ['|', '|',
                       ('partner_shipping_id.city', 'ilike', ga),
                       ('partner_shipping_id.zip', 'ilike', ga),
                       ('partner_shipping_id.country_id.name', 'ilike', ga)]
        orders = self.env['sale.order'].search(domain)
        grouped = {}
        for o in orders:
            area = o.partner_shipping_id.city or o.partner_shipping_id.zip or (
                o.partner_shipping_id.country_id.name if o.partner_shipping_id.country_id else _('Unknown')
            )
            if area not in grouped:
                grouped[area] = {'quotes': 0, 'won': 0, 'total': 0.0}
            grouped[area]['quotes'] += 1
            if o.state in ('sale', 'done'):
                grouped[area]['won'] += 1
            grouped[area]['total'] += (o.amount_total or 0.0)
        headers = [_('Geographic area'), _('Quotes'), _('Won orders'), _('Conversion %'), _('Revenue')]
        rows = []
        for area, g in sorted(grouped.items(), key=lambda x: x[0] or ''):
            conv = (g['won'] / g['quotes'] * 100.0) if g['quotes'] else 0.0
            rows.append([area, g['quotes'], g['won'], '%.1f' % conv, '%.2f' % g['total']])
        if not rows:
            rows = [[_('No commercial data for selected area/period.')]]
        return {'title': _('Commercial Performance by Geographic Area'), 'headers': headers, 'rows': rows}

    def _get_data_combined_article_site_supplier(self):
        """Article consumption by site and supplier."""
        domain = []
        if self.company_id:
            domain.append(('site_id.company_id', '=', self.company_id.id))
        consumptions = self.env['btp.site.consumption'].search(domain)
        headers = [_('Site'), _('Article'), _('Supplier'), _('Planned'), _('Actual'), _('Variance')]
        rows = []
        for c in consumptions:
            supplier_names = ', '.join(c.product_id.seller_ids.mapped('partner_id.name')) if c.product_id else ''
            variance = (c.real_qty or 0.0) - (c.planned_qty or 0.0)
            rows.append([
                c.site_id.name or '',
                c.product_id.name if c.product_id else '',
                supplier_names,
                '%.2f' % (c.planned_qty or 0.0),
                '%.2f' % (c.real_qty or 0.0),
                '%.2f' % variance,
            ])
        if not rows:
            rows = [[_('No consumption data.')]]
        return {'title': _('Article Consumption by Site & Supplier'), 'headers': headers, 'rows': rows}

    def _get_data_combined_margin_salesperson_client(self):
        """Net margin by salesperson and client (site-level)."""
        domain = [('btp_site_code', '!=', False)]
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        sites = self.env['project.project'].search(domain)
        grouped = {}
        for s in sites:
            salesperson = s.user_id.name if s.user_id else _('No salesperson')
            client = s.partner_id.name if s.partner_id else _('No client')
            key = (salesperson, client)
            if key not in grouped:
                grouped[key] = {'sites': 0, 'margin': 0.0, 'invoiced': 0.0}
            grouped[key]['sites'] += 1
            grouped[key]['margin'] += (s.btp_net_margin or 0.0)
            grouped[key]['invoiced'] += (s.btp_invoiced_total or 0.0)
        headers = [_('Salesperson'), _('Client'), _('Sites'), _('Invoiced'), _('Net Margin')]
        rows = []
        for (salesperson, client), g in sorted(grouped.items(), key=lambda x: (x[0][0], x[0][1])):
            rows.append([salesperson, client, g['sites'], '%.2f' % g['invoiced'], '%.2f' % g['margin']])
        if not rows:
            rows = [[_('No margin data.')]]
        return {'title': _('Net Margin by Salesperson & Client'), 'headers': headers, 'rows': rows}

    def _get_data_qhse_incidents(self):
        """QHSE incidents by site."""
        domain = []
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        incident_type_labels = dict(
            self.env['btp.qse.incident']._fields['incident_type'].selection
        )
        severity_labels = dict(
            self.env['btp.qse.incident']._fields['severity'].selection
        )
        incidents = self.env['btp.qse.incident'].search(domain, order='site_id, date desc')
        headers = [_('Site'), _('Date'), _('Type'), _('Severity'), _('Status'), _('Description')]
        rows = []
        for i in incidents:
            rows.append([
                i.site_id.name if i.site_id else '',
                i.date.strftime('%Y-%m-%d') if i.date else '',
                incident_type_labels.get(i.incident_type, i.incident_type) if i.incident_type else '',
                severity_labels.get(i.severity, i.severity) if i.severity else '',
                i.state or '',
                (i.description or '')[:80],
            ])
        if not rows:
            rows = [[_('No incidents.')]]
        return {'title': _('QHSE Incidents by Site'), 'headers': headers, 'rows': rows}

    def _get_data_margin_consumption_combined(self):
        """Net margin by site and article consumption summary."""
        domain = [('btp_site_code', '!=', False)]
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        sites = self.env['project.project'].search(domain, order='btp_site_code')
        headers = [_('Site'), _('Quote Total'), _('Invoiced'), _('Costs'), _('Net Margin'), _('Margin %')]
        rows = []
        for s in sites:
            rows.append([
                s.name or '',
                '%.2f' % (s.btp_quote_total or 0),
                '%.2f' % (s.btp_invoiced_total or 0),
                '%.2f' % (s.btp_actual_costs or 0),
                '%.2f' % (s.btp_net_margin or 0),
                '%.1f' % (s.btp_margin_percent or 0),
            ])
        if not rows:
            rows = [[_('No sites.')]]
        return {'title': _('Net Margin & Article Consumption'), 'headers': headers, 'rows': rows}

    # ---------- Module 13 — Multi-companies consolidation ----------

    def _get_data_consolidated_turnover(self):
        """Turnover (CA) by company and consolidated total (sale orders converted)."""
        domain = [('state', 'in', ('sale', 'done'))]
        if self.date_from:
            domain.append(('date_order', '>=', self.date_from))
        if self.date_to:
            domain.append(('date_order', '<=', self.date_to))
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        orders = self.env['sale.order'].search(domain)
        by_company = {}
        for o in orders:
            cid = o.company_id.id if o.company_id else 0
            cname = o.company_id.name if o.company_id else _('No company')
            if cid not in by_company:
                by_company[cid] = {'name': cname, 'total': 0.0}
            by_company[cid]['total'] += o.amount_untaxed or 0
        headers = [_('Company'), _('Turnover (HT)')]
        rows = [[v['name'], '%.2f' % v['total']] for _k, v in sorted(by_company.items(), key=lambda x: x[1]['name'])]
        total = sum(v['total'] for v in by_company.values())
        if rows:
            rows.append([_('Total (consolidated)'), '%.2f' % total])
        if not rows:
            rows = [[_('No data for the selected period.')]]
        return {'title': _('Consolidated Turnover by Company'), 'headers': headers, 'rows': rows}

    def _get_data_consolidated_cash(self):
        """Invoiced amounts by company (posted out_invoice) and consolidated total."""
        domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
        ]
        if self.date_from:
            domain.append(('invoice_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('invoice_date', '<=', self.date_to))
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        moves = self.env['account.move'].search(domain)
        by_company = {}
        for m in moves:
            cid = m.company_id.id if m.company_id else 0
            cname = m.company_id.name if m.company_id else _('No company')
            if cid not in by_company:
                by_company[cid] = {'name': cname, 'total': 0.0}
            by_company[cid]['total'] += m.amount_untaxed or 0
        headers = [_('Company'), _('Invoiced Total (HT)')]
        rows = [[v['name'], '%.2f' % v['total']] for _k, v in sorted(by_company.items(), key=lambda x: x[1]['name'])]
        total = sum(v['total'] for v in by_company.values())
        if rows:
            rows.append([_('Total (consolidated)'), '%.2f' % total])
        if not rows:
            rows = [[_('No invoices for the selected period.')]]
        return {'title': _('Consolidated Cash / Invoiced by Company'), 'headers': headers, 'rows': rows}

    def _get_data_consolidated_margin(self):
        """Net margin by company and by site, with consolidated total."""
        domain = [('btp_site_code', '!=', False)]
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        sites = self.env['project.project'].search(domain, order='company_id, btp_site_code')
        if self.date_from or self.date_to:
            def _site_ref_date(site):
                return site.btp_end_date_actual or site.btp_start_date or (
                    site.create_date.date() if site.create_date else False
                )

            sites = sites.filtered(
                lambda s: (
                    _site_ref_date(s)
                    and (not self.date_from or _site_ref_date(s) >= self.date_from)
                    and (not self.date_to or _site_ref_date(s) <= self.date_to)
                )
            )
        by_company = {}
        for s in sites:
            cid = s.company_id.id if s.company_id else 0
            cname = s.company_id.name if s.company_id else _('No company')
            if cid not in by_company:
                by_company[cid] = {'name': cname, 'sites': [], 'margin': 0.0}
            by_company[cid]['sites'].append(s)
            by_company[cid]['margin'] += s.btp_net_margin or 0
        headers = [_('Company'), _('Site'), _('Net Margin'), _('Margin %')]
        rows = []
        grand_total = 0.0
        for cid, v in sorted(by_company.items(), key=lambda x: x[1]['name']):
            for site in v['sites']:
                rows.append([
                    v['name'],
                    site.name or site.btp_site_code or '',
                    '%.2f' % (site.btp_net_margin or 0),
                    '%.1f' % (site.btp_margin_percent or 0),
                ])
            rows.append([v['name'], _('Subtotal'), '%.2f' % v['margin'], ''])
            grand_total += v['margin']
        if rows:
            rows.append([_('Total (consolidated)'), '', '%.2f' % grand_total, ''])
        if not rows:
            rows = [[_('No sites.')]]
        return {'title': _('Consolidated Net Margin by Company & Site'), 'headers': headers, 'rows': rows}

    def _get_data_shared_clients_distribution(self):
        """Distribution of shared clients: client name and list of companies sharing it."""
        partners = self.env['res.partner'].search(
            [('is_company', '=', True)],
            order='name',
        ).filtered(lambda p: p.btp_shared_company_ids)
        headers = [_('Client'), _('Shared with companies')]
        rows = []
        for p in partners:
            company_names = p.btp_shared_company_ids.mapped('name')
            rows.append([p.name or _('Unnamed'), ', '.join(company_names) if company_names else ''])
        if not rows:
            rows = [[_('No shared clients.')]]
        return {'title': _('Shared Clients Distribution'), 'headers': headers, 'rows': rows}

    def _get_data_data_quality(self):
        """Module 15: Data quality KPIs — duplicates detected, documentary conformity."""
        Partner = self.env['res.partner']
        # Potential duplicate contacts
        dup_contacts = Partner.search_count([
            ('is_company', '=', False),
            ('btp_duplicate_warning', '=', True),
        ])
        # Suppliers/subcontractors with expired docs
        expired_suppliers = Partner.search_count([
            ('is_company', '=', True),
            ('btp_conformity_status', '=', 'expired'),
        ])
        # Total suppliers/subcontractors with documents (for conformity rate)
        with_docs = Partner.search([
            ('is_company', '=', True),
            ('is_supplier', '=', True),
            '|', ('is_subcontractor', '=', True), ('is_supplier', '=', True),
        ])
        with_docs = with_docs.filtered(lambda p: p.btp_supplier_document_ids)
        total = len(with_docs)
        conform = total - len(with_docs.filtered(lambda p: p.btp_conformity_status == 'expired'))
        rate = (100.0 * conform / total) if total else 100.0
        headers = [_('Indicator'), _('Value')]
        rows = [
            [_('Potential duplicate contacts'), str(dup_contacts)],
            [_('Suppliers with expired documents'), str(expired_suppliers)],
            [_('Documentary conformity rate (%)'), '%.1f' % rate],
        ]
        return {'title': _('Data Quality'), 'headers': headers, 'rows': rows}

    def _get_data_governance_reattributions(self):
        """Module 15: List of client/contact reattributions (who, when, why)."""
        domain = []
        if self.date_from:
            domain.append(('change_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('change_date', '<=', self.date_to))
        reattributions = self.env['btp.company.reattribution'].search(
            domain, order='change_date desc', limit=500
        )
        headers = [_('Date'), _('Partner'), _('From'), _('To'), _('By'), _('Reason')]
        rows = []
        for r in reattributions:
            rows.append([
                r.change_date.strftime('%Y-%m-%d %H:%M') if r.change_date else '',
                r.partner_id.name or '',
                r.old_user_id.name or _('Unassigned'),
                r.new_user_id.name or _('Unassigned'),
                r.changed_by_id.name or '',
                (r.reason or '')[:80],
            ])
        if not rows:
            rows = [[_('No reattributions in the selected period.')]]
        return {'title': _('Reattributions'), 'headers': headers, 'rows': rows}

    def _render_pdf(self, data):
        """Generate PDF using QWeb report (template fetches data via doc._get_report_data())."""
        report = self.env.ref('btp_prospecting.action_report_btp_generic', raise_if_not_found=False)
        if report:
            pdf, _ = report._render_qweb_pdf(report.id, self.ids)
            filename = (self.name or 'report').replace(' ', '_') + '.pdf'
            import base64
            return base64.b64encode(pdf), filename, 'application/pdf'
        raise UserError(_('PDF report template not found. Use CSV or Excel format.'))

    def _render_xlsx(self, data):
        """Generate Excel file."""
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_('Excel export requires the xlsxwriter Python library.'))
        import base64
        import io
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet((data.get('title') or 'Report')[:31])
        bold = workbook.add_format({'bold': True})
        headers = data.get('headers') or []
        rows = data.get('rows') or []
        for col, h in enumerate(headers):
            sheet.write(0, col, h, bold)
        for row_idx, row in enumerate(rows, start=1):
            for col_idx, cell in enumerate(row):
                sheet.write(row_idx, col_idx, cell)
        workbook.close()
        output.seek(0)
        filename = (self.name or 'report').replace(' ', '_') + '.xlsx'
        return base64.b64encode(output.getvalue()), filename, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def _render_csv(self, data):
        """Generate CSV file."""
        import base64
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        headers = data.get('headers') or []
        rows = data.get('rows') or []
        if headers:
            writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
        content = output.getvalue().encode('utf-8-sig')  # BOM for Excel
        filename = (self.name or 'report').replace(' ', '_') + '.csv'
        return base64.b64encode(content), filename, 'text/csv'
