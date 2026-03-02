# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 15 — Synthesis & System Governance: audit trail for sensitive actions.

from odoo import models, fields, api


class BtpAuditLog(models.Model):
    _name = 'btp.audit.log'
    _description = 'BTP Audit Log'
    _order = 'create_date desc, id desc'

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        ondelete='restrict',
    )
    action = fields.Selection([
        ('create', 'Create'),
        ('write', 'Update'),
        ('unlink', 'Delete'),
        ('reattribution', 'Reattribution'),
        ('force_duplicate', 'Force Duplicate'),
        ('merge', 'Merge'),
    ], string='Action', required=True)
    model_name = fields.Char(string='Model', index=True)
    res_id = fields.Integer(string='Record ID')
    reason = fields.Text(string='Reason / Notes')
    create_date = fields.Datetime(string='Date', readonly=True)

    @api.model
    def log(self, action, model_name=None, res_id=None, reason=None):
        """Create an audit log entry. Use from write/create/unlink overrides."""
        return self.sudo().create({
            'user_id': self.env.user.id,
            'action': action,
            'model_name': model_name,
            'res_id': res_id,
            'reason': reason or '',
        })
