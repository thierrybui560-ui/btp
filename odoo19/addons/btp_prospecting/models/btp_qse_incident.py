# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 10 — Quality & Safety (QHSE)

from odoo import models, fields, api, _

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
        string='Photos / Attachments',
        compute='_compute_attachment_ids',
        help='Photos or documents attached to the declaration. Use the Chatter below to add files (drag and drop supported).',
    )

    @api.depends('message_ids')
    def _compute_attachment_ids(self):
        for record in self:
            # Direct attachments on the record (res_model/res_id)
            direct = self.env['ir.attachment'].search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id),
            ])
            # Attachments on chatter messages (drag-and-drop in Chatter)
            from_messages = self.env['ir.attachment'].search([
                ('res_model', '=', 'mail.message'),
                ('res_id', 'in', record.message_ids.ids),
            ])
            record.attachment_ids = direct | from_messages
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
        return super().create(vals_list)

    def action_assign_me(self):
        self.ensure_one()
        self.responsible_id = self.env.user.id
        self.state = 'in_progress'

    def action_close(self):
        for record in self:
            if record.state != 'closed':
                record.write({
                    'state': 'closed',
                    'closed_date': fields.Date.today(),
                })

    def action_reopen(self):
        self.write({
            'state': 'in_progress',
            'closed_date': False,
        })
