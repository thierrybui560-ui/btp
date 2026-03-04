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
    btp_yield_alert_threshold = fields.Float(
        string='Yield alert threshold (%)',
        config_parameter='btp_prospecting.btp_yield_alert_threshold',
        default=80.0,
        help='Yield below this percentage is flagged as an alert.',
    )
    btp_yield_escalation_days = fields.Integer(
        string='Yield escalation delay (days)',
        config_parameter='btp_prospecting.btp_yield_escalation_days',
        default=2,
        help='Number of days a low-yield alert can remain open before management escalation.',
    )
    btp_default_internal_hourly_cost = fields.Float(
        string='Default internal hourly cost',
        config_parameter='btp_prospecting.btp_default_internal_hourly_cost',
        default=0.0,
        help='Fallback internal labor hourly cost used in site margin computations.',
    )
    btp_default_subcontractor_hourly_cost = fields.Float(
        string='Default subcontractor hourly cost',
        config_parameter='btp_prospecting.btp_default_subcontractor_hourly_cost',
        default=0.0,
        help='Fallback subcontractor labor hourly cost used in site margin computations.',
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
    btp_ai_enabled = fields.Boolean(
        string='Enable AI external calls',
        config_parameter='btp_prospecting.btp_ai_enabled',
        default=True,
        help='Global kill-switch for external AI provider calls.',
    )
    btp_ai_daily_request_limit = fields.Integer(
        string='AI max requests per day',
        config_parameter='btp_prospecting.btp_ai_daily_request_limit',
        default=200,
        help='Maximum number of AI requests per company per day. Set 0 for unlimited.',
    )
