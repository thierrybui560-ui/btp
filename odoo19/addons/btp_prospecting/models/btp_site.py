# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model
    def get_views(self, views, options=None):
        """Normalize legacy view type 'tree' to 'list' so Odoo 19 finds the list view."""
        if views:
            views = [(v_id, 'list' if v_type == 'tree' else v_type) for v_id, v_type in views]
        return super().get_views(views, options=options)

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        """Treat legacy view type 'tree' as 'list' (Odoo 19 has no view type 'tree')."""
        if view_type == 'tree':
            view_type = 'list'
        return super()._get_view(view_id=view_id, view_type=view_type, **options)

    btp_site_code = fields.Char(
        string='Site Code',
        copy=False,
        readonly=True,
        index=True,
        help='Site code in format YYYYMMNNN'
    )
    btp_site_address = fields.Char(string='Site Address')
    btp_site_city = fields.Char(string='City')
    btp_site_zip = fields.Char(string='ZIP')
    btp_site_country_id = fields.Many2one('res.country', string='Country')
    btp_site_latitude = fields.Float(string='Latitude')
    btp_site_longitude = fields.Float(string='Longitude')
    btp_start_date = fields.Date(string='Start Date')
    btp_end_date_planned = fields.Date(string='Planned End Date')
    btp_end_date_actual = fields.Date(string='Actual End Date')

    btp_client_contact_ids = fields.Many2many(
        'res.partner',
        'btp_project_contact_rel',
        'project_id',
        'contact_id',
        string='Client Contacts',
        domain="[('is_company', '=', False)]"
    )
    btp_subcontractor_ids = fields.Many2many(
        'res.partner',
        'btp_site_subcontractor_rel',
        'project_id',
        'partner_id',
        string='Subcontractors',
        domain="[('is_company', '=', True), ('is_subcontractor', '=', True)]"
    )
    btp_supplier_ids = fields.Many2many(
        'res.partner',
        'btp_site_supplier_rel',
        'project_id',
        'partner_id',
        string='Suppliers',
        domain="[('is_company', '=', True), ('is_supplier', '=', True)]"
    )
    btp_employee_ids = fields.Many2many(
        'res.users',
        'btp_site_employee_rel',
        'project_id',
        'user_id',
        string='Assigned Employees'
    )
    btp_sale_order_id = fields.Many2one(
        'sale.order',
        string='Source Quote/Order',
        copy=False,
        ondelete='set null'
    )
    btp_document_ids = fields.One2many(
        'btp.site.document',
        'site_id',
        string='Documents'
    )
    btp_document_requirement_ids = fields.One2many(
        'btp.site.document.requirement',
        'site_id',
        string='Document Checklist'
    )
    btp_missing_document_count = fields.Integer(
        string='Missing Documents',
        compute='_compute_document_status',
        store=True
    )
    btp_expired_document_count = fields.Integer(
        string='Expired Documents',
        compute='_compute_document_status',
        store=True
    )
    btp_is_blocked = fields.Boolean(
        string='Blocked',
        compute='_compute_document_status',
        store=True,
        help='True when mandatory documents are missing or expired.'
    )
    btp_planning_task_count = fields.Integer(
        string='Planning Tasks',
        compute='_compute_btp_planning_task_count',
        store=False,
        help='Number of tasks linked to quote items (from Generate planning).'
    )
    # Module 7 - Invoicing & Situations
    btp_retention_rate = fields.Float(
        string='Retention Rate %',
        digits=(5, 2),
        default=5.0,
        help='Retention of guarantee rate applied to situations/invoices (default 5%).'
    )
    btp_retention_release_date = fields.Date(
        string='Retention Release Date',
        help='Planned release of retained amounts (e.g. 12 months after site reception).'
    )
    btp_situation_ids = fields.One2many(
        'btp.situation',
        'site_id',
        string='Situations',
        copy=False,
    )
    btp_invoice_ids = fields.One2many(
        'account.move',
        'btp_site_id',
        string='Invoices',
        copy=False,
        domain=[('move_type', '=', 'out_invoice')],
    )
    btp_consumption_ids = fields.One2many(
        'btp.site.consumption',
        'site_id',
        string='Consumptions',
        help='Article consumptions on site (for actual costs in margin).',
    )
    btp_invoice_count = fields.Integer(
        string='Invoices',
        compute='_compute_btp_invoice_count',
        store=False,
    )
    btp_has_final_invoice = fields.Boolean(
        string='Has Final Invoice',
        compute='_compute_btp_has_final_invoice',
        store=False,
    )
    # Module 8 — Payments & Finances: analytical margin by site
    btp_quote_total = fields.Float(
        string='Quote Total (Forecast)',
        digits='Product Price',
        compute='_compute_btp_margin_fields',
        store=True,
        help='Total HT from source quote (forecast revenue).',
    )
    btp_invoiced_total = fields.Float(
        string='Invoiced Total',
        digits='Product Price',
        compute='_compute_btp_margin_fields',
        store=True,
        help='Sum of posted customer invoices for this site.',
    )
    btp_actual_costs = fields.Float(
        string='Actual Costs',
        digits='Product Price',
        compute='_compute_btp_margin_fields',
        store=True,
        help='Costs from consumptions (actual qty × product cost) and pointing (labor/subcontracting).',
    )
    btp_net_margin = fields.Float(
        string='Net Margin',
        digits='Product Price',
        compute='_compute_btp_margin_fields',
        store=True,
        help='Invoiced total minus actual costs.',
    )
    btp_margin_percent = fields.Float(
        string='Margin %',
        digits=(5, 2),
        compute='_compute_btp_margin_fields',
        store=True,
        help='Net margin as percentage of invoiced total.',
    )

    @api.depends('btp_sale_order_id', 'btp_sale_order_id.amount_total',
                 'btp_invoice_ids', 'btp_invoice_ids.state', 'btp_invoice_ids.amount_total',
                 'btp_consumption_ids', 'btp_consumption_ids.real_qty', 'btp_consumption_ids.product_id')
    def _compute_btp_margin_fields(self):
        for site in self:
            quote_total = 0.0
            if site.btp_sale_order_id:
                quote_total = site.btp_sale_order_id.amount_total or 0.0
            site.btp_quote_total = quote_total
            invoiced = sum(
                site.btp_invoice_ids.filtered(lambda m: m.state == 'posted').mapped('amount_total')
            )
            site.btp_invoiced_total = invoiced
            costs = site._btp_actual_costs_compute()
            site.btp_actual_costs = costs
            site.btp_net_margin = invoiced - costs
            if invoiced and (invoiced - costs) is not None:
                site.btp_margin_percent = ((invoiced - costs) / invoiced) * 100.0
            else:
                site.btp_margin_percent = 0.0

    def _btp_actual_costs_compute(self):
        """Actual costs from consumptions (real_qty × product cost). Pointing/labor can be extended later."""
        self.ensure_one()
        cost = 0.0
        consumptions = self.env['btp.site.consumption'].search([('site_id', '=', self.id)])
        for c in consumptions:
            price = c.product_id.standard_price if c.product_id else 0.0
            cost += (c.real_qty or 0.0) * price
        return cost

    @api.depends('btp_invoice_ids', 'btp_invoice_ids.btp_invoice_type', 'btp_invoice_ids.state')
    def _compute_btp_has_final_invoice(self):
        for site in self:
            site.btp_has_final_invoice = bool(
                site.btp_invoice_ids.filtered(
                    lambda m: m.btp_invoice_type == 'final' and m.state != 'cancel'
                )
            )

    @api.depends('btp_invoice_ids')
    def _compute_btp_invoice_count(self):
        for site in self:
            site.btp_invoice_count = len(site.btp_invoice_ids)

    @api.depends('task_ids', 'task_ids.btp_quote_item_id')
    def _compute_btp_planning_task_count(self):
        for site in self:
            site.btp_planning_task_count = len(site.task_ids.filtered('btp_quote_item_id'))

    def action_btp_generate_planning(self):
        """Generate Gantt tasks from the site's source quote items (Lot → Title → Subtitle → Item)."""
        self.ensure_one()
        if not self.btp_sale_order_id:
            raise UserError(_('This site has no source quote. Link a quote (Source Quote/Order) first, or create a site from an accepted quote.'))
        order = self.btp_sale_order_id
        items = self.env['btp.quote.item']
        for lot in order.btp_lot_ids:
            for title in lot.title_ids:
                for subtitle in title.subtitle_ids:
                    items |= subtitle.item_ids
        if not items:
            raise UserError(_('The source quote has no items. Add Lot → Title → Subtitle → Item structure first.'))
        # Avoid duplicates: do not create a task for an item already linked to a task of this project
        existing_item_ids = self.task_ids.mapped('btp_quote_item_id').ids
        to_create = items.filtered(lambda i: i.id not in existing_item_ids)
        if not to_create:
            raise UserError(_('Planning already generated for all quote items. Delete existing planning tasks if you want to regenerate.'))
        start = self.btp_start_date or fields.Date.today()
        end = self.btp_end_date_planned or (start + timedelta(days=30))
        if isinstance(start, str):
            start = fields.Date.from_string(start)
        if isinstance(end, str):
            end = fields.Date.from_string(end)
        total_days = max(1, (end - start).days)
        day_per_item = total_days / len(to_create) if to_create else 0
        Task = self.env['project.task']
        for seq, item in enumerate(to_create.sorted(lambda i: (i.lot_id.sequence, i.title_id.sequence, i.subtitle_id.sequence, i.sequence)), 1):
            item_start = start + timedelta(days=round((seq - 1) * day_per_item))
            item_end = start + timedelta(days=round(seq * day_per_item))
            date_assign = datetime.combine(item_start, datetime.min.time()) if item_start else False
            date_deadline = datetime.combine(item_end, datetime.min.time()) if item_end else False
            vals = Task._btp_from_quote_item_vals(item, self, seq * 10, date_assign, date_deadline)
            Task.create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'list,form,calendar',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_btp_new_situation(self):
        """Create a new monthly situation (draft) with lines from the site's quote."""
        self.ensure_one()
        if not self.btp_sale_order_id:
            raise UserError(_('Link a Source Quote/Order to the site first.'))
        order = self.btp_sale_order_id
        items = self.env['btp.quote.item']
        for lot in order.btp_lot_ids:
            for title in lot.title_ids:
                for subtitle in title.subtitle_ids:
                    items |= subtitle.item_ids
        if not items:
            raise UserError(_('The source quote has no items.'))
        # Default situation date = last day of current month
        today = fields.Date.today()
        from dateutil.relativedelta import relativedelta
        end_of_month = today + relativedelta(day=31)
        situation_date = end_of_month
        # Check not already existing
        existing = self.env['btp.situation'].search([
            ('site_id', '=', self.id),
            ('situation_date', '=', situation_date),
        ], limit=1)
        if existing:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'btp.situation',
                'res_id': existing.id,
                'view_mode': 'form',
            }
        line_vals = []
        for seq, item in enumerate(items.sorted(
            lambda i: (i.lot_id.sequence, i.title_id.sequence, i.subtitle_id.sequence, i.sequence)
        ), 1):
            total = item.subtotal or 0.0
            line_vals.append((0, 0, {
                'quote_item_id': item.id,
                'sequence': seq * 10,
                'total_amount': total,
                'cumul_m_prev': 0.0,
                'cumul_m': 0.0,
            }))
        situation = self.env['btp.situation'].create({
            'site_id': self.id,
            'situation_date': situation_date,
            'line_ids': line_vals,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'btp.situation',
            'res_id': situation.id,
            'view_mode': 'form',
        }

    def action_btp_view_invoices(self):
        """Open BTP invoices for this site."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'name': _('Site Invoices'),
            'view_mode': 'list,form',
            'domain': [('btp_site_id', '=', self.id), ('move_type', '=', 'out_invoice')],
            'context': {'default_btp_site_id': self.id, 'default_move_type': 'out_invoice'},
        }

    def action_btp_create_deposit_invoice(self):
        """Open wizard to create a deposit invoice for this site."""
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_('Site must have a client (Partner) set.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Deposit Invoice'),
            'res_model': 'btp.deposit.invoice.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_model': 'project.project', 'active_id': self.id},
        }

    def action_btp_create_final_invoice(self):
        """Create a single final invoice from the site's quote (one-shot invoicing)."""
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_('Site must have a client (Partner) set.'))
        order = self.btp_sale_order_id
        if not order:
            raise UserError(_('Site must have a linked Sale Order for final invoicing.'))
        existing = self.env['account.move'].search([
            ('btp_site_id', '=', self.id),
            ('btp_invoice_type', '=', 'final'),
            ('state', '!=', 'cancel'),
        ], limit=1)
        if existing:
            raise UserError(_('A final invoice already exists for this site: %s.') % existing.name)

        company = self.company_id or self.env.company
        journal = self.env['account.journal'].search([
            ('company_id', '=', company.id),
            ('type', '=', 'sale'),
        ], limit=1)
        if not journal:
            raise UserError(_('No sales journal found for the company. Create a journal of type "Sales" in Accounting → Configuration → Journals for company "%s".') % (company.name or _('current')))
        btp_sequence = self.env['ir.sequence'].next_by_code(
            'btp.invoice',
            sequence_date=fields.Date.today(),
        )
        if not btp_sequence:
            raise UserError(_('BTP invoice sequence is not configured.'))

        product = self.env.ref(
            'btp_prospecting.product_btp_quote_item_service_template',
            raise_if_not_found=False,
        )
        product_id = product.product_variant_id if product else False
        account = False
        if product_id and product_id.property_account_income_id:
            account = product_id.property_account_income_id
        if not account:
            account = self.env['account.account'].search([
                ('company_ids', 'in', [company.id]),
                ('account_type', 'in', ('income', 'income_other')),
            ], limit=1)
        if not account:
            raise UserError(_(
                'No income account found for invoice lines. For company "%s", set an Income account on the BTP service product (Accounting tab) or ensure the Chart of Accounts has an account of type Income.'
            ) % (company.name or _('current')))

        items = self.env['btp.quote.item']
        for lot in order.btp_lot_ids:
            for title in lot.title_ids:
                for subtitle in title.subtitle_ids:
                    items |= subtitle.item_ids
        line_vals = []
        for item in items.sorted(
            lambda i: (i.lot_id.sequence, i.title_id.sequence, i.subtitle_id.sequence, i.sequence)
        ):
            amount = item.subtotal or 0.0
            if amount <= 0:
                continue
            line_vals.append((0, 0, {
                'name': item.name or _('Quote item'),
                'quantity': 1.0,
                'price_unit': amount,
                'account_id': account.id,
                'product_id': product_id.id if product_id else False,
            }))
        if not line_vals:
            raise UserError(_('The source quote has no positive amounts to invoice.'))

        retention_rate = self.btp_retention_rate or 0.0
        total_before_retention = sum(item.subtotal or 0.0 for item in items)
        retention_amount = total_before_retention * (retention_rate / 100.0)
        if retention_amount > 0:
            line_vals.append((0, 0, {
                'name': _('Retention of guarantee (%s%%)') % retention_rate,
                'quantity': 1.0,
                'price_unit': -retention_amount,
                'account_id': account.id,
                'product_id': product_id.id if product_id else False,
            }))

        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'ref': _('Final invoice - %s') % (self.name or self.btp_site_code or ''),
            'btp_invoice_type': 'final',
            'btp_invoice_sequence': btp_sequence,
            'btp_site_id': self.id,
            'btp_retention_rate': retention_rate,
            'btp_retention_amount': retention_amount,
            'journal_id': journal.id,
            'invoice_line_ids': line_vals,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
            'context': {'default_move_type': 'out_invoice'},
        }

    @api.depends(
        'btp_document_requirement_ids',
        'btp_document_requirement_ids.is_mandatory',
        'btp_document_requirement_ids.missing',
        'btp_document_requirement_ids.expired',
    )
    def _compute_document_status(self):
        for site in self:
            required = site.btp_document_requirement_ids.filtered('is_mandatory')
            site.btp_missing_document_count = len(required.filtered('missing'))
            site.btp_expired_document_count = len(required.filtered('expired'))
            site.btp_is_blocked = bool(site.btp_missing_document_count or site.btp_expired_document_count)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('btp_site_code'):
                vals['btp_site_code'] = self._generate_site_code()
        return super().create(vals_list)

    def _generate_site_code(self):
        sequence = self.env['ir.sequence'].next_by_code(
            'btp.site',
            sequence_date=fields.Date.today(),
        )
        if not sequence:
            raise UserError(_('Site sequence is not configured.'))
        return sequence
