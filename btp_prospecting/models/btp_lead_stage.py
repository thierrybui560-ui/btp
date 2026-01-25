# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BtpLeadStage(models.Model):
    """Lead Stage Model - Defines the pipeline workflow"""
    _name = 'btp.lead.stage'
    _description = 'BTP Lead Stage'
    _order = 'sequence, id'
    
    name = fields.Char(string='Stage Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10, help='Order of stages')
    fold = fields.Boolean(
        string='Folded in Pipeline',
        help='Leads in this stage are folded in the kanban view'
    )
    require_reminder = fields.Boolean(
        string='Require Reminder',
        default=True,
        help='If True, next_reminder_date is mandatory when lead enters this stage'
    )
    qualification_status = fields.Selection([
        ('field', 'Field'),
        ('targeting', 'Targeting'),
        ('contact', 'Contact'),
        ('decision', 'Decision'),
    ], string='Qualification Status',
       help='Default qualification status for leads in this stage')
    
    # Visual
    color = fields.Integer(string='Color', default=10)
    
    # Conversion
    is_won = fields.Boolean(
        string='Won Stage',
        help='Leads in this stage are considered won/converted'
    )
    is_lost = fields.Boolean(
        string='Lost Stage',
        help='Leads in this stage are considered lost'
    )
    
    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        help='If set, this stage is only available for this company'
    )
    
    # Statistics
    lead_count = fields.Integer(
        string='Lead Count',
        compute='_compute_lead_count'
    )
    
    @api.depends('name')
    def _compute_lead_count(self):
        for stage in self:
            stage.lead_count = self.env['btp.lead'].search_count([
                ('stage_id', '=', stage.id)
            ])
    
    @api.constrains('is_won', 'is_lost')
    def _check_won_lost(self):
        for stage in self:
            if stage.is_won and stage.is_lost:
                raise ValidationError(_('A stage cannot be both won and lost.'))


class BtpLeadAssignmentRule(models.Model):
    """Lead Assignment Rules - Automatically assign leads based on criteria"""
    _name = 'btp.lead.assignment.rule'
    _description = 'BTP Lead Assignment Rule'
    _order = 'sequence, id'
    
    name = fields.Char(string='Rule Name', required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(string='Priority', default=10, help='Lower number = higher priority')
    
    # Assignment
    user_id = fields.Many2one(
        'res.users',
        string='Assign To',
        required=True,
        help='User to assign leads to'
    )
    team_id = fields.Many2one(
        'crm.team',
        string='Sales Team',
        help='Sales team for this rule'
    )
    
    # Criteria
    assignment_type = fields.Selection([
        ('geography', 'Geography'),
        ('client_type', 'Client Type'),
        ('site_type', 'Site Type'),
        ('round_robin', 'Round Robin'),
        ('manual', 'Manual Only'),
    ], string='Assignment Type', required=True, default='manual')
    
    # Geography criteria
    country_ids = fields.Many2many(
        'res.country',
        'btp_rule_country_rel',
        'rule_id',
        'country_id',
        string='Countries',
        help='Assign leads from these countries'
    )
    city_names = fields.Text(
        string='Cities',
        help='City names (one per line) to match leads from. Leave empty to match all cities.'
    )
    zip_code_pattern = fields.Char(
        string='ZIP Code Pattern',
        help='ZIP code pattern (e.g., "75*" for Paris area)'
    )
    
    # Client type criteria
    partner_category_ids = fields.Many2many(
        'res.partner.category',
        'btp_rule_partner_category_rel',
        'rule_id',
        'category_id',
        string='Client Categories',
        help='Assign leads with clients in these categories'
    )
    
    # Site type criteria
    site_type = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('public_works', 'Public Works'),
        ('infrastructure', 'Infrastructure'),
        ('renovation', 'Renovation'),
        ('other', 'Other'),
    ], string='Site Type', help='Assign leads with this site type')
    
    # Round robin
    round_robin_count = fields.Integer(
        string='Round Robin Count',
        default=0,
        help='Current count for round-robin distribution'
    )
    
    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        help='If set, this rule only applies to this company'
    )
    
    # Limits
    max_leads_per_month = fields.Integer(
        string='Max Leads per Month',
        help='Maximum number of leads to assign per month (0 = unlimited)'
    )
    current_month_count = fields.Integer(
        string='Current Month Count',
        compute='_compute_month_count',
        help='Number of leads assigned this month'
    )
    
    @api.depends('user_id')
    def _compute_month_count(self):
        for rule in self:
            if rule.max_leads_per_month:
                month_start = fields.Datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                rule.current_month_count = self.env['btp.lead'].search_count([
                    ('assignment_rule_id', '=', rule.id),
                    ('create_date', '>=', month_start),
                ])
            else:
                rule.current_month_count = 0
    
    def match(self, vals):
        """Check if lead values match this rule"""
        self.ensure_one()
        
        if not self.active:
            return False
        
        # Check company
        company_id = vals.get('company_id', self.env.company.id)
        if self.company_id and self.company_id.id != company_id:
            return False
        
        # Check limits
        if self.max_leads_per_month and self.current_month_count >= self.max_leads_per_month:
            return False
        
        # Manual only - don't auto-assign
        if self.assignment_type == 'manual':
            return False
        
        # Geography
        if self.assignment_type == 'geography':
            if self.country_ids:
                country_id = vals.get('site_country_id')
                if not country_id or country_id not in self.country_ids.ids:
                    return False
            
            if self.city_names:
                city_names = [c.strip().lower() for c in self.city_names.split('\n') if c.strip()]
                lead_city = vals.get('site_city', '').strip().lower()
                if not lead_city or lead_city not in city_names:
                    return False
            
            if self.zip_code_pattern:
                zip_code = vals.get('site_zip', '')
                if not zip_code or not self._match_pattern(zip_code, self.zip_code_pattern):
                    return False
        
        # Client type
        elif self.assignment_type == 'client_type':
            if self.partner_category_ids:
                partner_id = vals.get('partner_id')
                if partner_id:
                    partner = self.env['res.partner'].browse(partner_id)
                    if not (partner.category_id & self.partner_category_ids):
                        return False
                else:
                    return False
        
        # Site type
        elif self.assignment_type == 'site_type':
            site_type = vals.get('site_type')
            if not site_type or site_type != self.site_type:
                return False
        
        # Round robin - always matches if no other criteria
        elif self.assignment_type == 'round_robin':
            # Round robin logic would be handled separately
            pass
        
        return True
    
    def _match_pattern(self, value, pattern):
        """Match value against pattern (supports * wildcard)"""
        import re
        pattern_re = pattern.replace('*', '.*')
        return bool(re.match(pattern_re, value))
    
    def assign_round_robin(self):
        """Assign lead using round-robin"""
        self.ensure_one()
        if self.assignment_type != 'round_robin':
            return False

        pool = self._get_round_robin_pool()
        if not pool:
            return False

        # Increment counter only when a valid pool exists
        self.write({'round_robin_count': self.round_robin_count + 1})
        index = (self.round_robin_count - 1) % len(pool)
        return pool[index]

    def _get_round_robin_pool(self):
        """Build weighted pool of available users for round-robin"""
        self.ensure_one()

        if self.team_id:
            candidates = self.team_id.member_ids.filtered(
                lambda u: u.has_group('btp_prospecting.group_btp_salesperson')
            )
        else:
            candidates = self.user_id

        if not candidates:
            return []

        available = candidates.filtered(lambda u: not u.btp_is_unavailable and not u.btp_is_overloaded)
        if not available:
            return []

        weighted_pool = []
        for user in available:
            weight = max(user.btp_round_robin_weight or 1, 1)
            weighted_pool.extend([user] * weight)

        return weighted_pool

