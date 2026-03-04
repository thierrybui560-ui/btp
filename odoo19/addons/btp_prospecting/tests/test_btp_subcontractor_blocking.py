# -*- coding: utf-8 -*-

import base64
from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestBtpSubcontractorBlocking(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env['res.partner']
        cls.Doc = cls.env['btp.supplier.document']
        cls.Attachment = cls.env['ir.attachment']

    def _create_attachment(self, name):
        return self.Attachment.create({
            'name': name,
            'type': 'binary',
            'datas': base64.b64encode(b'dummy'),
            'res_model': 'res.partner',
            'res_id': 0,
            'mimetype': 'text/plain',
        })

    def _create_doc(self, partner, doc_type, exp_days=30):
        attach = self._create_attachment('%s-%s.txt' % (partner.id, doc_type))
        return self.Doc.create({
            'name': doc_type,
            'supplier_id': partner.id,
            'document_type': doc_type,
            'issue_date': fields.Date.today(),
            'expiration_date': fields.Date.today() + timedelta(days=exp_days),
            'attachment_id': attach.id,
        })

    def test_subcontractor_document_validation(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'btp_prospecting.btp_subcontractor_blocking_enabled', 'True'
        )
        subcontractor = self.Partner.create({
            'name': 'Sub A',
            'is_company': True,
            'company_type': 'company',
            'is_subcontractor': True,
        })
        for doc_type in ['urssaf', 'taxes', 'insurance', 'paid_vacations']:
            self._create_doc(subcontractor, doc_type, exp_days=30)
        subcontractor._btp_validate_subcontractor_documents_or_raise()

        # Expire one mandatory document -> must block
        subcontractor.btp_supplier_document_ids.filtered(
            lambda d: d.document_type == 'urssaf'
        ).write({'expiration_date': fields.Date.today() - timedelta(days=1)})
        with self.assertRaises(ValidationError):
            subcontractor._btp_validate_subcontractor_documents_or_raise()
