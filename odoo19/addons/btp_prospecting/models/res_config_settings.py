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
    # Module 15 — System Governance: automatic reattribution
    btp_reattribution_inactive_days = fields.Integer(
        string='Inactive client reattribution (days)',
        config_parameter='btp_prospecting.btp_reattribution_inactive_days',
        default=30,
        help='After this many days without activity, unmonitored clients/prospects can be reattributed to the manager.',
    )
    btp_automatic_reattribution_enabled = fields.Boolean(
        string='Enable automatic client reattribution',
        config_parameter='btp_prospecting.btp_automatic_reattribution_enabled',
        default=False,
        help='When enabled, clients with no activity for the configured number of days are reattributed to the salesperson\'s manager.',
    )
