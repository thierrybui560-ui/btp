# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class BtpArticleDocument(models.Model):
    """Document attached to an article (TS, PV, SDS, notices)"""
    _name = 'btp.article.document'
    _description = 'Article Document'
    _order = 'article_id, document_type, issue_date desc'

    name = fields.Char(
        string='Document Name',
        required=True,
        help='Name of the document'
    )
    article_id = fields.Many2one(
        'product.template',
        string='Article',
        required=True,
        ondelete='cascade',
        index=True
    )
    document_type = fields.Selection([
        ('ts', 'Technical Sheet'),
        ('pv', 'Test Report (PV)'),
        ('sds', 'Safety Data Sheet (SDS)'),
        ('notice', 'Usage Notice'),
        ('other', 'Other'),
    ], string='Document Type',
        required=True,
        default='ts',
        help='Type of document'
    )
    reference = fields.Char(
        string='Reference',
        help='Document reference number'
    )
    issue_date = fields.Date(
        string='Issue Date',
        default=fields.Date.today,
        help='Date when the document was issued'
    )
    expiration_date = fields.Date(
        string='Expiration Date',
        help='Date when the document expires (if applicable)'
    )
    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Attachment',
        required=True,
        ondelete='cascade',
        help='File attachment'
    )
    is_expired = fields.Boolean(
        string='Is Expired',
        compute='_compute_is_expired',
        store=True,
        help='Document has expired'
    )
    expires_soon = fields.Boolean(
        string='Expires Soon',
        compute='_compute_expires_soon',
        store=True,
        help='Document expires within 30 days'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    description = fields.Text(
        string='Description',
        help='Additional notes about the document'
    )

    @api.depends('expiration_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for record in self:
            record.is_expired = record.expiration_date and record.expiration_date < today

    @api.depends('expiration_date')
    def _compute_expires_soon(self):
        today = fields.Date.today()
        warning_date = today + timedelta(days=30)
        for record in self:
            record.expires_soon = (
                record.expiration_date and
                not record.is_expired and
                record.expiration_date <= warning_date
            )

    @api.constrains('expiration_date', 'issue_date')
    def _check_dates(self):
        for record in self:
            if record.expiration_date and record.issue_date:
                if record.expiration_date < record.issue_date:
                    raise ValidationError(_('Expiration date must be after issue date.'))

    @api.model
    def _check_document_expiration(self):
        """Cron job: Check for expiring documents and create activities"""
        today = fields.Date.today()
        warning_date = today + timedelta(days=30)
        
        # Find documents expiring soon or expired
        expiring_docs = self.search([
            ('expiration_date', '<=', warning_date),
            ('expiration_date', '>=', today),
            ('active', '=', True),
        ])
        
        expired_docs = self.search([
            ('expiration_date', '<', today),
            ('active', '=', True),
        ])
        
        # Create activities for expiring documents
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if activity_type:
            for doc in expiring_docs:
                # Check if activity already exists
                existing = self.env['mail.activity'].search([
                    ('res_model', '=', 'product.template'),
                    ('res_id', '=', doc.article_id.id),
                    ('activity_type_id', '=', activity_type.id),
                    ('summary', 'ilike', f'Document {doc.name}'),
                ], limit=1)
                
                if not existing:
                    self.env['mail.activity'].create({
                        'res_model': 'product.template',
                        'res_id': doc.article_id.id,
                        'activity_type_id': activity_type.id,
                        'summary': _('Document "%s" expires on %s') % (doc.name, doc.expiration_date),
                        'note': _('Document type: %s\nReference: %s') % (dict(doc._fields['document_type'].selection)[doc.document_type], doc.reference or 'N/A'),
                        'date_deadline': doc.expiration_date,
                        'user_id': doc.article_id.create_uid.id or self.env.user.id,
                    })
            
            # Create activities for expired documents
            for doc in expired_docs:
                existing = self.env['mail.activity'].search([
                    ('res_model', '=', 'product.template'),
                    ('res_id', '=', doc.article_id.id),
                    ('activity_type_id', '=', activity_type.id),
                    ('summary', 'ilike', f'Document {doc.name} EXPIRED'),
                ], limit=1)
                
                if not existing:
                    self.env['mail.activity'].create({
                        'res_model': 'product.template',
                        'res_id': doc.article_id.id,
                        'activity_type_id': activity_type.id,
                        'summary': _('Document "%s" EXPIRED on %s') % (doc.name, doc.expiration_date),
                        'note': _('Document type: %s\nReference: %s\n⚠️ This document has expired!') % (dict(doc._fields['document_type'].selection)[doc.document_type], doc.reference or 'N/A'),
                        'date_deadline': doc.expiration_date,
                        'user_id': doc.article_id.create_uid.id or self.env.user.id,
                    })
        
        return len(expiring_docs) + len(expired_docs)

