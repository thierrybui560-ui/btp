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
    ('conformity_pv', 'Conformity PV'),
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
    name_normalized = fields.Char(
        string='Name (normalized)',
        compute='_compute_name_normalized',
        store=True,
        index=True,
        help='Lowercased and stripped name for version chain matching (same name = same chain regardless of case).'
    )
    site_id = fields.Many2one(
        'project.project',
        string='Site',
        required=True,
        ondelete='cascade',
        index=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='site_id.company_id',
        store=True,
        readonly=True,
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
    article_id = fields.Many2one(
        'product.template',
        string='Article',
        domain="[('is_btp_article', '=', True)]",
        ondelete='set null',
        help='Article linked to this QHSE/technical document (datasheet, PV, notice, etc.).',
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

    @api.model
    def _btp_category_from_type(self, document_type):
        """Return default category for a given document type."""
        if document_type in {'ppsps', 'diuo', 'authorization', 'safety_certificate', 'certificate', 'conformity_pv', 'site_pv'}:
            return 'regulatory'
        if document_type in {'plan', 'doe', 'notice', 'photo'}:
            return 'technical'
        if document_type in {'client_contract', 'subcontractor_contract', 'amendment'}:
            return 'contract'
        return False

    @api.depends('version')
    def _compute_version_label(self):
        for record in self:
            record.version_label = f"V{record.version or 1}"

    @api.depends('name')
    def _compute_name_normalized(self):
        for record in self:
            record.name_normalized = (record.name or '').strip().lower() or False

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

    @api.depends('site_id', 'document_type', 'name', 'name_normalized', 'version')
    def _compute_is_latest_version(self):
        for record in self:
            if not record.site_id:
                record.is_latest_version = False
                continue
            name_norm = record.name_normalized or (record.name or '').strip().lower() or False
            if not name_norm:
                record.is_latest_version = False
                continue
            domain = [
                ('site_id', '=', record.site_id.id),
                ('document_type', '=', record.document_type),
                ('name_normalized', '=', name_norm),
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
        chain_versions = {}
        for vals in vals_list:
            # Keep category consistent with type so records appear in expected site tabs
            # (e.g. PPSPS/Safety Certificate should always be visible in Safety tab).
            inferred_category = self._btp_category_from_type(vals.get('document_type'))
            if inferred_category:
                vals['category'] = inferred_category

            name_norm = (vals.get('name') or '').strip().lower() or False
            key = (vals.get('site_id'), vals.get('document_type'), name_norm)
            if all(key):
                if key not in chain_versions:
                    last = self.with_context(active_test=False).search([
                        ('site_id', '=', key[0]),
                        ('document_type', '=', key[1]),
                        ('name_normalized', '=', name_norm),
                    ], order='version desc', limit=1)
                    chain_versions[key] = last.version or 0
                next_version = chain_versions[key] + 1

                # Forms/one2many views often submit default version=1.
                # Force monotonic versioning for same (site, type, name) chain.
                requested_version = vals.get('version')
                if not requested_version or requested_version <= chain_versions[key]:
                    vals['version'] = next_version
                chain_versions[key] = vals.get('version') or next_version
        records = super().create(vals_list)
        records.with_context(btp_skip_version_chain=True)._btp_recompute_version_chain()
        return records

    def write(self, vals):
        if self.env.context.get('btp_skip_version_chain'):
            return super().write(vals)

        # Archived versions are consultable but not modifiable.
        if any(not rec.active for rec in self):
            editable_keys = set(vals.keys()) - {'active'}
            if editable_keys:
                raise ValidationError(_('Archived document versions are read-only. Create a new version instead.'))

        # Keep category coherent when type changes from form/list edits.
        if vals.get('document_type'):
            inferred_category = self._btp_category_from_type(vals.get('document_type'))
            if inferred_category:
                vals = dict(vals)
                vals['category'] = inferred_category
        res = super().write(vals)
        # Recompute only when a chain-defining field changes.
        if any(k in vals for k in ('active', 'site_id', 'document_type', 'name', 'version')):
            self.with_context(btp_skip_version_chain=True)._btp_recompute_version_chain()
        return res

    def _btp_recompute_version_chain(self):
        """Ensure exactly one active latest record per (site, type, name_normalized) chain."""
        if not self:
            return
        processed = set()
        for rec in self:
            name_norm = rec.name_normalized or (rec.name or '').strip().lower() or False
            if not name_norm:
                continue
            key = (rec.site_id.id, rec.document_type, name_norm)
            if not rec.site_id.id or key in processed:
                continue
            processed.add(key)
            chain = self.with_context(active_test=False).search([
                ('site_id', '=', rec.site_id.id),
                ('document_type', '=', rec.document_type),
                ('name_normalized', '=', name_norm),
            ], order='version desc, id desc')
            if not chain:
                continue
            latest = chain[:1]
            old = chain - latest
            old_to_archive = old.filtered(lambda r: r.active)
            if old_to_archive:
                old_to_archive.with_context(btp_skip_version_chain=True).write({'active': False})
            latest_to_activate = latest.filtered(lambda r: not r.active)
            if latest_to_activate:
                latest_to_activate.with_context(btp_skip_version_chain=True).write({'active': True})

    @api.model
    def _check_document_expiration(self):
        """Run with sudo so all companies' documents are considered (cron runs as scheduler user)."""
        today = fields.Date.today()
        warning_date = today + timedelta(days=self._get_expiration_warning_days())

        expiring = self.sudo().search([
            ('expiration_date', '<=', warning_date),
            ('expiration_date', '>=', today),
            ('active', '=', True),
        ])
        expired = self.sudo().search([
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
        if not doc.site_id or not doc.site_id.id:
            return
        summary = f'{label}: {doc.name}'
        existing = self.env['mail.activity'].sudo().search([
            ('res_model', '=', 'project.project'),
            ('res_id', '=', doc.site_id.id),
            ('activity_type_id', '=', activity_type.id),
            ('summary', '=', summary),
        ], limit=1)
        if existing:
            return
        self.env['mail.activity'].sudo().create({
            'res_model_id': self.env['ir.model']._get('project.project').id,
            'res_id': doc.site_id.id,
            'activity_type_id': activity_type.id,
            'summary': summary,
            'date_deadline': doc.expiration_date or fields.Date.today(),
            'user_id': doc.site_id.user_id.id or self.env.user.id,
            'note': _(
                '%s for site %s (type: %s).'
            ) % (label, doc.site_id.display_name, doc.document_type),
        })
