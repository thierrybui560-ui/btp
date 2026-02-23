# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


DOCUMENT_CATEGORY = [
    ('contract', 'Contracts'),
    ('regulatory', 'Regulatory'),
    ('technical', 'Technical'),
    ('supplier', 'Supplier/Subcontractor'),
    ('misc', 'Miscellaneous'),
]

DOCUMENT_TYPE = [
    ('client_contract', 'Client Contract'),
    ('subcontractor_contract', 'Subcontractor Contract'),
    ('amendment', 'Amendment'),
    ('ppsps', 'PPSPS'),
    ('diuo', 'DIUO'),
    ('authorization', 'Authorization'),
    ('safety_certificate', 'Safety Certificate'),
    ('plan', 'Plan'),
    ('doe', 'DOE'),
    ('notice', 'Article Notice'),
    ('delivery_note', 'Delivery Note'),
    ('certificate', 'Certificate'),
    ('photo', 'Photo'),
    ('meeting_minutes', 'Meeting Minutes'),
    ('site_pv', 'Site PV'),
    ('other', 'Other'),
]


class BtpSiteDocument(models.Model):
    _name = 'btp.site.document'
    _description = 'Site Document'
    _order = 'site_id, document_type, version desc, id desc'

    name = fields.Char(
        string='Document Name',
        required=True
    )
    site_id = fields.Many2one(
        'project.project',
        string='Site',
        required=True,
        ondelete='cascade',
        index=True
    )
    category = fields.Selection(
        DOCUMENT_CATEGORY,
        string='Category',
        required=True,
        default='technical'
    )
    document_type = fields.Selection(
        DOCUMENT_TYPE,
        string='Document Type',
        required=True
    )
    version = fields.Integer(
        string='Version',
        default=1
    )
    version_label = fields.Char(
        string='Version Label',
        compute='_compute_version_label',
        store=True
    )
    issue_date = fields.Date(
        string='Issue Date',
        default=fields.Date.today
    )
    expiration_date = fields.Date(
        string='Expiration Date'
    )
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Attachment',
        ondelete='cascade'
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain="[('is_company', '=', True), ('is_supplier', '=', True)]",
        ondelete='set null'
    )
    subcontractor_id = fields.Many2one(
        'res.partner',
        string='Subcontractor',
        domain="[('is_company', '=', True), ('is_subcontractor', '=', True)]",
        ondelete='set null'
    )
    quote_item_id = fields.Many2one(
        'btp.quote.item',
        string='Quote Item',
        ondelete='set null'
    )
    quote_id = fields.Many2one(
        'sale.order',
        string='Quote/Order',
        ondelete='set null'
    )
    active = fields.Boolean(default=True)
    is_expired = fields.Boolean(
        string='Is Expired',
        compute='_compute_is_expired',
        store=True
    )
    expires_soon = fields.Boolean(
        string='Expires Soon',
        compute='_compute_expires_soon',
        store=True
    )
    is_latest_version = fields.Boolean(
        string='Latest Version',
        compute='_compute_is_latest_version',
        store=True
    )
    notes = fields.Text(string='Notes')

    @api.depends('version')
    def _compute_version_label(self):
        for record in self:
            record.version_label = f"V{record.version or 1}"

    def _get_expiration_warning_days(self):
        value = self.env['ir.config_parameter'].sudo().get_param(
            'btp_prospecting.btp_document_expiration_days',
            default='30',
        )
        try:
            return int(value)
        except (TypeError, ValueError):
            return 30

    @api.depends('expiration_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for record in self:
            record.is_expired = bool(record.expiration_date and record.expiration_date < today)

    @api.depends('expiration_date')
    def _compute_expires_soon(self):
        today = fields.Date.today()
        warning_date = today + timedelta(days=self._get_expiration_warning_days())
        for record in self:
            record.expires_soon = bool(
                record.expiration_date and not record.is_expired and record.expiration_date <= warning_date
            )

    @api.depends('site_id', 'document_type', 'name', 'version')
    def _compute_is_latest_version(self):
        for record in self:
            if not record.site_id:
                record.is_latest_version = False
                continue
            domain = [
                ('site_id', '=', record.site_id.id),
                ('document_type', '=', record.document_type),
                ('name', '=', record.name),
            ]
            latest = self.search(domain, order='version desc', limit=1)
            record.is_latest_version = latest.id == record.id

    @api.constrains('expiration_date', 'issue_date')
    def _check_dates(self):
        for record in self:
            if record.expiration_date and record.issue_date:
                if record.expiration_date < record.issue_date:
                    raise ValidationError(_('Expiration date must be after issue date.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('version'):
                domain = [
                    ('site_id', '=', vals.get('site_id')),
                    ('document_type', '=', vals.get('document_type')),
                    ('name', '=', vals.get('name')),
                ]
                last = self.search(domain, order='version desc', limit=1)
                vals['version'] = (last.version or 0) + 1 if last else 1
        records = super().create(vals_list)
        for record in records:
            domain = [
                ('id', '!=', record.id),
                ('site_id', '=', record.site_id.id),
                ('document_type', '=', record.document_type),
                ('name', '=', record.name),
            ]
            self.search(domain).write({'active': False})
        return records

    @api.model
    def _check_document_expiration(self):
        today = fields.Date.today()
        warning_date = today + timedelta(days=self._get_expiration_warning_days())

        expiring = self.search([
            ('expiration_date', '<=', warning_date),
            ('expiration_date', '>=', today),
            ('active', '=', True),
        ])
        expired = self.search([
            ('expiration_date', '<', today),
            ('active', '=', True),
        ])

        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return

        for doc in expiring:
            self._create_site_activity(doc, activity_type, 'Document expiring soon')

        for doc in expired:
            self._create_site_activity(doc, activity_type, 'Document expired')

    def _create_site_activity(self, doc, activity_type, label):
        summary = f'{label}: {doc.name}'
        existing = self.env['mail.activity'].search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', doc.site_id.id),
            ('activity_type_id', '=', activity_type.id),
            ('summary', '=', summary),
        ], limit=1)
        if existing:
            return
        self.env['mail.activity'].create({
            'res_model': 'project.project',
            'res_id': doc.site_id.id,
            'activity_type_id': activity_type.id,
            'summary': summary,
            'date_deadline': doc.expiration_date or fields.Date.today(),
            'user_id': doc.site_id.user_id.id or self.env.user.id,
            'note': _(
                '%s for site %s (type: %s).'
            ) % (label, doc.site_id.display_name, doc.document_type),
        })
