# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = 'project.project'

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
