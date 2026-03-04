# -*- coding: utf-8 -*-

from odoo import api, fields, models


class BtpRagDocument(models.Model):
    _name = 'btp.rag.document'
    _description = 'BTP RAG Document'
    _order = 'id desc'

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        index=True,
    )
    source_model = fields.Char(required=True)
    source_res_id = fields.Integer(required=True, index=True)
    text_content = fields.Text()
    active = fields.Boolean(default=True)
    chunk_ids = fields.One2many('btp.rag.chunk', 'document_id')
    chunk_count = fields.Integer(compute='_compute_chunk_count')

    _sql_constraints = [
        (
            'btp_rag_document_source_unique',
            'unique(source_model, source_res_id)',
            'A source record can only be indexed once.',
        ),
    ]

    @api.depends('chunk_ids')
    def _compute_chunk_count(self):
        for rec in self:
            rec.chunk_count = len(rec.chunk_ids)

    def reindex_chunks(self, chunk_size=1000):
        for doc in self:
            doc.chunk_ids.unlink()
            text = doc.text_content or ''
            parts = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)] if text else []
            for idx, part in enumerate(parts, 1):
                self.env['btp.rag.chunk'].create({
                    'document_id': doc.id,
                    'sequence': idx,
                    'content': part,
                    'token_estimate': max(1, len(part) // 4),
                })

    @api.model
    def _cron_refresh_rag_index(self):
        docs = self.search([('active', '=', True)], limit=500)
        docs.reindex_chunks()
        return len(docs)
