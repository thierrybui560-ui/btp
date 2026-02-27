# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 11 — Reports & Exports

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

REPORT_SCOPE = [
    ('commercial_leads_quotes', 'Leads & Quotes by Salesperson'),
    ('site_progress', 'Site Progress, Costs & Margins'),
    ('client_volume', 'Business Volume by Client'),
    ('salesperson_activity', 'Salesperson Activity (leads, quotes, conversion)'),
    ('article_consumption', 'Article Consumption (planned vs actual)'),
    ('supplier_analysis', 'Supplier / Price Analysis'),
    ('qhse_incidents', 'QHSE Incidents by Site'),
    ('margin_consumption_combined', 'Net Margin & Article Consumption'),
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
    company_id = fields.Many2one(
        'res.company',
        string='Company',
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
        """Run templates that are due (daily / weekly / monthly)."""
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
            elif t.schedule == 'weekly' and weekday == 0:
                due = True
            elif t.schedule == 'monthly' and day_of_month == 1:
                due = True
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
        leads = self.env['btp.lead'].search([('converted', '=', True)])
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
        sites = self.env['project.project'].search(domain, order='btp_site_code')
        headers = [
            _('Site Code'), _('Site Name'), _('Quote Total'), _('Invoiced'), _('Actual Costs'),
            _('Net Margin'), _('Margin %'),
        ]
        rows = []
        for s in sites:
            rows.append([
                s.btp_site_code or '',
                s.name or '',
                '%.2f' % (s.btp_quote_total or 0),
                '%.2f' % (s.btp_invoiced_total or 0),
                '%.2f' % (s.btp_actual_costs or 0),
                '%.2f' % (s.btp_net_margin or 0),
                '%.1f' % (s.btp_margin_percent or 0),
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
        orders = self.env['sale.order'].search(domain, order='partner_id')
        by_partner = {}
        for o in orders:
            p = o.partner_id
            key = (p.id, p.name if p else _('No client'))
            if key not in by_partner:
                by_partner[key] = {'name': key[1], 'orders': 0, 'total': 0.0}
            by_partner[key]['orders'] += 1
            by_partner[key]['total'] += o.amount_total or 0
        headers = [_('Client'), _('Orders'), _('Total amount')]
        rows = [[v['name'], v['orders'], '%.2f' % v['total']] for _, v in sorted(by_partner.items(), key=lambda x: x[1]['name'])]
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
        orders = self.env['sale.order'].search([
            ('btp_quote_number', '!=', False),
            ('state', 'in', ('sale', 'done')),
        ])
        for o in orders:
            u = o.user_id
            key = (u.id if u else 0, u.name if u else _('No user'))
            if key not in by_user:
                by_user[key] = {'name': key[1], 'leads': 0, 'converted': 0, 'quotes_won': 0}
            by_user[key]['quotes_won'] = by_user[key].get('quotes_won', 0) + 1
        headers = [_('Salesperson'), _('Leads'), _('Converted'), _('Quotes won'), _('Conversion %')]
        rows = []
        for (_, name), v in sorted(by_user.items(), key=lambda x: x[0][1] or ''):
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
        headers = [_('Supplier'), _('Article'), _('Date'), _('Price'), _('Quantity')]
        rows = []
        for h in history:
            rows.append([
                h.supplier_id.name if h.supplier_id else '',
                h.article_id.name if h.article_id else '',
                h.purchase_date.strftime('%Y-%m-%d') if h.purchase_date else '',
                '%.2f' % (h.purchase_price or 0),
                '%.2f' % (h.quantity or 0),
            ])
        if not rows:
            rows = [[_('No price history.')]]
        return {'title': _('Supplier / Price Analysis'), 'headers': headers, 'rows': rows}

    def _get_data_qhse_incidents(self):
        """QHSE incidents by site."""
        domain = []
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        incidents = self.env['btp.qse.incident'].search(domain, order='site_id, date desc')
        headers = [_('Site'), _('Date'), _('Type'), _('Status'), _('Description')]
        rows = []
        for i in incidents:
            rows.append([
                i.site_id.name if i.site_id else '',
                i.date.strftime('%Y-%m-%d') if i.date else '',
                dict(REPORT_SCOPE).get(i.incident_type, i.incident_type) if i.incident_type else '',
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
