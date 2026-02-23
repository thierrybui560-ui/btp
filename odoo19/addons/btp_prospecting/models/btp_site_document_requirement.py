# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .btp_site_document import DOCUMENT_CATEGORY, DOCUMENT_TYPE


class BtpSiteDocumentRequirement(models.Model):
    _name = 'btp.site.document.requirement'
    _description = 'Site Document Requirement'
    _order = 'site_id, document_type'

    site_id = fields.Many2one(
        'project.project',
        string='Site',
        required=True,
        ondelete='cascade'
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
    is_mandatory = fields.Boolean(
        string='Mandatory',
        default=True
    )
    required_before_start = fields.Boolean(
        string='Required Before Start',
        default=False
    )
    last_document_id = fields.Many2one(
        'btp.site.document',
        string='Latest Document',
        compute='_compute_status',
        store=True
    )
    missing = fields.Boolean(
        string='Missing',
        compute='_compute_status',
        store=True
    )
    expired = fields.Boolean(
        string='Expired',
        compute='_compute_status',
        store=True
    )
    fulfilled = fields.Boolean(
        string='Fulfilled',
        compute='_compute_status',
        store=True
    )

    @api.depends(
        'site_id',
        'document_type',
        'site_id.btp_document_ids',
        'site_id.btp_document_ids.document_type',
        'site_id.btp_document_ids.is_expired',
        'site_id.btp_document_ids.active',
        'site_id.btp_document_ids.version',
    )
    def _compute_status(self):
        for req in self:
            if not req.site_id:
                req.last_document_id = False
                req.missing = True
                req.expired = False
                req.fulfilled = False
                continue
            docs = req.site_id.btp_document_ids.filtered(
                lambda d: d.document_type == req.document_type and d.active
            )
            latest = docs.sorted(key=lambda d: d.version or 0, reverse=True)[:1]
            latest_doc = latest[0] if latest else False
            req.last_document_id = latest_doc
            req.missing = not bool(latest_doc)
            req.expired = bool(latest_doc and latest_doc.is_expired)
            req.fulfilled = bool(latest_doc and not latest_doc.is_expired)
