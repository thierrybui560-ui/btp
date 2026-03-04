# -*- coding: utf-8 -*-

from odoo import fields, models


class BtpRagChunk(models.Model):
    _name = 'btp.rag.chunk'
    _description = 'BTP RAG Chunk'
    _order = 'document_id, sequence'

    document_id = fields.Many2one('btp.rag.document', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='document_id.company_id',
        store=True,
        readonly=True,
        index=True,
    )
    sequence = fields.Integer(default=10)
    content = fields.Text(required=True)
    token_estimate = fields.Integer(default=0)
    embedding_key = fields.Char(
        help='Placeholder for external vector index identifier when using a vector store.',
    )
