# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 10 — Quality & Safety (QHSE)

from odoo import models, fields, api

CORRECTIVE_ACTION_STATE = [
    ('open', 'Open'),
    ('done', 'Done'),
]


class BtpQseCorrectiveAction(models.Model):
    _name = 'btp.qse.corrective.action'
    _description = 'QHSE Corrective Action'
    _order = 'deadline asc, id asc'

    incident_id = fields.Many2one(
        'btp.qse.incident',
        string='Incident',
        required=True,
        ondelete='cascade',
        index=True,
    )
    site_id = fields.Many2one(
        'project.project',
        string='Site',
        related='incident_id.site_id',
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='incident_id.company_id',
        store=True,
        readonly=True,
    )
    name = fields.Char(
        string='Action',
        required=True,
    )
    description = fields.Text(string='Description')
    assigned_to_id = fields.Many2one(
        'res.users',
        string='Assigned To',
        ondelete='set null',
    )
    deadline = fields.Date(string='Deadline')
    state = fields.Selection(
        CORRECTIVE_ACTION_STATE,
        string='Status',
        default='open',
        required=True,
    )
    done_date = fields.Date(string='Done Date', readonly=True)

    def action_done(self):
        for record in self:
            if record.state == 'open':
                record.write({
                    'state': 'done',
                    'done_date': fields.Date.today(),
                })

    def action_reopen(self):
        self.write({
            'state': 'open',
            'done_date': False,
        })
