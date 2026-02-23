# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    btp_subcontractor_blocking_enabled = fields.Boolean(
        string='Block operations when subcontractor documents are invalid',
        config_parameter='btp_prospecting.btp_subcontractor_blocking_enabled',
        default=False,
        help='When enabled, operations involving subcontractors with expired or missing '
             'documents may be blocked.',
    )
    btp_document_expiration_days = fields.Integer(
        string='Document expiration warning (days)',
        config_parameter='btp_prospecting.btp_document_expiration_days',
        default=30,
        help='Number of days before expiration to flag subcontractor documents as expiring soon.',
    )
