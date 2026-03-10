# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 10 — Quality & Safety (QHSE)

from odoo import models, fields, api, _
from odoo.exceptions import UserError

INCIDENT_TYPE = [
    ('incident', 'Incident'),
    ('accident', 'Accident'),
    ('near_miss', 'Near Miss'),
    ('non_conformity', 'Non-Conformity'),
]

INCIDENT_STATE = [
    ('new', 'New'),
    ('in_progress', 'In Progress'),
    ('closed', 'Closed'),
]

INCIDENT_SEVERITY = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]


class BtpQseIncident(models.Model):
    _name = 'btp.qse.incident'
    _description = 'QHSE Incident / Non-Conformity'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    site_id = fields.Many2one(
        'project.project',
        string='Site',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
        domain=[('btp_site_code', '!=', False)],
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='site_id.company_id',
        store=True,
        readonly=True,
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    description = fields.Text(
        string='Description',
        required=True,
        tracking=True,
    )
    incident_type = fields.Selection(
        INCIDENT_TYPE,
        string='Type',
        required=True,
        default='incident',
        tracking=True,
    )
    severity = fields.Selection(
        INCIDENT_SEVERITY,
        string='Severity',
        required=True,
        default='medium',
        tracking=True,
    )
    location = fields.Char(
        string='Location on Site',
        help='Optional precise location where the incident occurred.',
    )
    concerned_team = fields.Char(
        string='Concerned Team',
        help='Team or persons concerned.',
    )
    state = fields.Selection(
        INCIDENT_STATE,
        string='Status',
        default='new',
        required=True,
        tracking=True,
        copy=False,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Reported By',
        default=lambda self: self.env.user,
        ondelete='set null',
        tracking=True,
    )
    responsible_id = fields.Many2one(
        'res.users',
        string='QHSE Responsible',
        ondelete='set null',
        tracking=True,
        help='User responsible for validation and corrective actions.',
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'btp_qse_incident_attachment_rel',
        'incident_id',
        'attachment_id',
        string='Photos / Attachments',
        help='Attach photos/documents directly in this section (drag and drop or browse).',
    )
    corrective_action_ids = fields.One2many(
        'btp.qse.corrective.action',
        'incident_id',
        string='Corrective Actions',
        copy=False,
    )
    corrective_action_count = fields.Integer(
        string='Corrective Actions',
        compute='_compute_corrective_action_count',
        store=True,
    )
    closed_date = fields.Date(
        string='Closed Date',
        readonly=True,
        copy=False,
    )
    notes = fields.Text(string='Internal Notes')

    @api.depends('corrective_action_ids')
    def _compute_corrective_action_count(self):
        for r in self:
            r.corrective_action_count = len(r.corrective_action_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq = self.env['ir.sequence'].next_by_code('btp.qse.incident') or _('New')
                vals['name'] = seq
        records = super().create(vals_list)
        records._sync_attachment_links()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'attachment_ids' in vals:
            self._sync_attachment_links()
        return res

    def _sync_attachment_links(self):
        """Bind uploaded attachments to this incident for coherent access/history."""
        for rec in self:
            to_link = rec.attachment_ids.filtered(
                lambda a: (not a.res_model or a.res_model == rec._name)
                and (not a.res_id or a.res_id == rec.id)
            )
            if to_link:
                to_link.sudo().write({'res_model': rec._name, 'res_id': rec.id})

    def action_assign_me(self):
        self.ensure_one()
        self.responsible_id = self.env.user.id
        self.state = 'in_progress'

    def action_close(self):
        for record in self:
            if record.state != 'closed':
                if not record.responsible_id:
                    raise UserError(_('Set a QHSE Responsible before closing the incident.'))
                if (
                    record.responsible_id != self.env.user
                    and not self.env.user.has_group('btp_prospecting.group_btp_manager')
                    and not self.env.user.has_group('btp_prospecting.group_btp_admin')
                ):
                    raise UserError(_('Only the QHSE Responsible or a Manager can close this incident.'))
                open_actions = record.corrective_action_ids.filtered(lambda a: a.state != 'done')
                if open_actions:
                    raise UserError(_('All corrective actions must be marked Done before closing the incident.'))
                record.write({
                    'state': 'closed',
                    'closed_date': fields.Date.today(),
                })

    def action_reopen(self):
        self.write({
            'state': 'in_progress',
            'closed_date': False,
        })
