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
