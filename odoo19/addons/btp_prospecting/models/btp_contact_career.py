# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class BtpContactCareer(models.Model):
    """Contact Career History - Tracks contact's career across companies"""
    _name = 'btp.contact.career'
    _description = 'BTP Contact Career History'
    _order = 'start_date desc, id desc'

    contact_id = fields.Many2one(
        'res.partner',
        string='Contact',
        required=True,
        ondelete='cascade',
        index=True,
        help='Contact person'
    )
    company_id = fields.Many2one(
        'res.partner',
        string='Company',
        required=True,
        domain="[('is_company', '=', True)]",
        help='Company where the contact worked/works'
    )
    job_title = fields.Char(
        string='Job Title',
        required=True,
        help='Position held at this company'
    )
    start_date = fields.Date(
        string='Start Date',
        required=True,
        help='Date when contact started at this company'
    )
    end_date = fields.Date(
        string='End Date',
        help='Date when contact left this company (empty if current)'
    )
    is_current = fields.Boolean(
        string='Current Position',
        compute='_compute_is_current',
        store=True,
        help='Is this the contact\'s current position?'
    )
    notes = fields.Text(
        string='Notes',
        help='Additional notes about this career period'
    )
    
    # Access tracking
    created_by = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )
    
    @api.depends('end_date')
    def _compute_is_current(self):
        for record in self:
            record.is_current = not record.end_date
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date and record.start_date:
                if record.end_date < record.start_date:
                    raise ValidationError(_('End date cannot be before start date.'))
    
    @api.model
    def create(self, vals):
        """When creating a career record, update contact's current company"""
        career = super(BtpContactCareer, self).create(vals)
        if career.is_current:
            # Update contact's current company (parent_id in res.partner)
            career.contact_id.with_context(skip_career_update=True).write({
                'parent_id': career.company_id.id,
                'function': career.job_title,
            })
        return career
    
    def write(self, vals):
        """When updating career, handle company changes"""
        result = super(BtpContactCareer, self).write(vals)
        for career in self:
            if career.is_current:
                # Update contact's current company (parent_id in res.partner)
                career.contact_id.with_context(skip_career_update=True).write({
                    'parent_id': career.company_id.id,
                    'function': career.job_title,
                })
        return result

