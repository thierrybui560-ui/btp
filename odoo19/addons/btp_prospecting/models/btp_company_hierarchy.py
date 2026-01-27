# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class BtpCompanyGroup(models.Model):
    """Company Group - Top level of hierarchy (e.g., Bouygues Construction)"""
    _name = 'btp.company.group'
    _description = 'BTP Company Group'
    _order = 'name'

    name = fields.Char(string='Group Name', required=True)
    siren = fields.Char(string='SIREN', size=9,
                       help='9-digit SIREN number (legal identifier at group level)')
    active = fields.Boolean(default=True)
    
    # Relations
    subsidiary_ids = fields.One2many(
        'btp.company.subsidiary',
        'group_id',
        string='Subsidiaries',
        help='Subsidiaries belonging to this group'
    )
    company_ids = fields.One2many(
        'res.partner',
        'btp_group_id',
        string='Companies',
        help='All companies in this group (including subsidiaries and agencies)'
    )
    
    # Statistics
    subsidiary_count = fields.Integer(
        string='Subsidiaries Count',
        compute='_compute_counts',
        store=False
    )
    company_count = fields.Integer(
        string='Companies Count',
        compute='_compute_counts',
        store=False
    )
    
    @api.depends('subsidiary_ids', 'company_ids')
    def _compute_counts(self):
        for record in self:
            record.subsidiary_count = len(record.subsidiary_ids)
            record.company_count = len(record.company_ids)
    
    def toggle_active(self):
        """Toggle active status"""
        for record in self:
            record.active = not record.active
    
    @api.constrains('siren')
    def _check_group_siren_unique(self):
        for record in self:
            if record.siren:
                duplicate = self.sudo().search([
                    ('id', '!=', record.id),
                    ('siren', '=', record.siren),
                ], limit=1)
                if duplicate:
                    raise ValidationError(_('SIREN must be unique.'))


class BtpCompanySubsidiary(models.Model):
    """Company Subsidiary - Second level (e.g., Bouygues Bâtiment Île-de-France)"""
    _name = 'btp.company.subsidiary'
    _description = 'BTP Company Subsidiary'
    _order = 'name'

    name = fields.Char(string='Subsidiary Name', required=True)
    siren = fields.Char(string='SIREN', size=9,
                       help='9-digit SIREN number (legal identifier)')
    active = fields.Boolean(default=True)
    
    # Hierarchy
    group_id = fields.Many2one(
        'btp.company.group',
        string='Group',
        required=True,
        ondelete='cascade',
        help='Parent group'
    )
    
    # Relations
    agency_ids = fields.One2many(
        'btp.company.agency',
        'subsidiary_id',
        string='Agencies',
        help='Agencies belonging to this subsidiary'
    )
    company_ids = fields.One2many(
        'res.partner',
        'btp_subsidiary_id',
        string='Companies',
        help='All companies in this subsidiary (including agencies)'
    )
    
    # Statistics
    agency_count = fields.Integer(
        string='Agencies Count',
        compute='_compute_counts',
        store=False
    )
    company_count = fields.Integer(
        string='Companies Count',
        compute='_compute_counts',
        store=False
    )
    
    @api.depends('agency_ids', 'company_ids')
    def _compute_counts(self):
        for record in self:
            record.agency_count = len(record.agency_ids)
            record.company_count = len(record.company_ids)
    
    def toggle_active(self):
        """Toggle active status"""
        for record in self:
            record.active = not record.active
    
    @api.constrains('siren')
    def _check_subsidiary_siren_unique(self):
        for record in self:
            if record.siren:
                duplicate = self.sudo().search([
                    ('id', '!=', record.id),
                    ('siren', '=', record.siren),
                ], limit=1)
                if duplicate:
                    raise ValidationError(_('SIREN must be unique.'))


class BtpCompanyAgency(models.Model):
    """Company Agency - Third level (e.g., Bouygues Bâtiment – West Agency)"""
    _name = 'btp.company.agency'
    _description = 'BTP Company Agency'
    _order = 'name'

    name = fields.Char(string='Agency Name', required=True)
    siret = fields.Char(string='SIRET', size=14,
                       help='14-digit SIRET number (legal identifier for agency)')
    active = fields.Boolean(default=True)
    
    # Hierarchy
    subsidiary_id = fields.Many2one(
        'btp.company.subsidiary',
        string='Subsidiary',
        required=True,
        ondelete='cascade',
        help='Parent subsidiary'
    )
    group_id = fields.Many2one(
        'btp.company.group',
        string='Group',
        related='subsidiary_id.group_id',
        store=True,
        readonly=True,
        help='Parent group (computed from subsidiary)'
    )
    
    # Relations
    company_ids = fields.One2many(
        'res.partner',
        'btp_agency_id',
        string='Companies',
        help='Companies attached to this agency'
    )
    
    # Statistics
    company_count = fields.Integer(
        string='Companies Count',
        compute='_compute_counts',
        store=False
    )
    
    @api.depends('company_ids')
    def _compute_counts(self):
        for record in self:
            record.company_count = len(record.company_ids)
    
    def toggle_active(self):
        """Toggle active status"""
        for record in self:
            record.active = not record.active
    
    @api.constrains('siret')
    def _check_agency_siret_unique(self):
        for record in self:
            if record.siret:
                duplicate = self.sudo().search([
                    ('id', '!=', record.id),
                    ('siret', '=', record.siret),
                ], limit=1)
                if duplicate:
                    raise ValidationError(_('SIRET must be unique.'))

