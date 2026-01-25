# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from markupsafe import Markup
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class BtpLead(models.Model):
    """BTP Lead Model - Core lead management for Building and Public Works industry"""
    _name = 'btp.lead'
    _description = 'BTP Lead'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'
    _rec_name = 'name'

    # ========== Basic Information ==========
    name = fields.Char(
        string='Lead Title',
        required=True,
        tracking=True,
        help='Title of the lead (e.g., "New apartment building in Paris needs fireproofing")'
    )
    active = fields.Boolean(default=True, tracking=True)
    
    # ========== Lead Origin & Source ==========
    origin = fields.Selection([
        ('field', 'Field Discovery'),
        ('web', 'Web Form'),
        ('social', 'Social Media'),
        ('partner', 'Partner'),
        ('ai', 'AI Auto-Search'),
        ('import', 'File Import'),
        ('manual', 'Manual Entry'),
        ('tender', 'Public Tender'),
        ('referral', 'Referral'),
        ('other', 'Other'),
    ], string='Origin', required=True, default='manual', tracking=True,
       help='Source where this lead was discovered')
    
    origin_detail = fields.Char(
        string='Origin Details',
        help='Additional details about the origin (e.g., specific website, partner name)'
    )
    
    # ========== Site Information (BTP Specific) ==========
    site_name = fields.Char(
        string='Site Name',
        tracking=True,
        help='Name of the construction site or project'
    )
    site_address = fields.Text(
        string='Site Address',
        tracking=True,
        help='Full address of the construction site'
    )
    site_city = fields.Char(string='City', tracking=True)
    site_zip = fields.Char(string='ZIP Code', tracking=True)
    site_country_id = fields.Many2one('res.country', string='Country', tracking=True)
    site_type = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('public_works', 'Public Works'),
        ('infrastructure', 'Infrastructure'),
        ('renovation', 'Renovation'),
        ('other', 'Other'),
    ], string='Site Type', tracking=True)
    
    # ========== Client/Prospect Information ==========
    partner_id = fields.Many2one(
        'res.partner',
        string='Client/Prospect',
        tracking=True,
        help='Client or prospect company'
    )
    contact_id = fields.Many2one(
        'res.partner',
        string='Contact Person',
        domain="[('is_company', '=', False)]",
        tracking=True,
        help='Primary contact person for this lead'
    )
    partner_name = fields.Char(
        string='Client Name',
        help='Name of the client if not yet in contacts'
    )
    partner_email = fields.Char(string='Email')
    partner_phone = fields.Char(string='Phone')
    
    # ========== Ownership & Attribution ==========
    user_id = fields.Many2one(
        'res.users',
        string='Assigned To',
        tracking=True,
        index=True,
        help='Salesperson assigned to this lead'
    )
    is_open = fields.Boolean(
        string='Common Open',
        default=False,
        tracking=True,
        help='If True, lead is visible to all salespeople until claimed'
    )
    claimed_date = fields.Datetime(
        string='Claimed Date',
        readonly=True,
        help='Date when lead was claimed by a salesperson'
    )
    assignment_rule_id = fields.Many2one(
        'btp.lead.assignment.rule',
        string='Assignment Rule',
        readonly=True,
        help='Rule that assigned this lead'
    )
    last_assigned_user_id = fields.Many2one(
        'res.users',
        string='Last Assigned To',
        readonly=True,
        help='Previous assignee used when reopening a common open lead'
    )

    @api.onchange('is_open')
    def _onchange_is_open(self):
        """When is_open is toggled, store previous assignee if needed"""
        for lead in self:
            if lead.is_open and lead.user_id:
                # Store previous assignee when making lead open
                lead.last_assigned_user_id = lead.user_id
            elif not lead.is_open and not lead.user_id and lead.last_assigned_user_id:
                # Restore previous assignee when unchecking open
                lead.user_id = lead.last_assigned_user_id

    @api.onchange('user_id')
    def _onchange_user_id(self):
        """When user_id is set, store it as last assigned"""
        for lead in self:
            if lead.user_id:
                lead.last_assigned_user_id = lead.user_id

    
    # ========== Qualification & Workflow ==========
    stage_id = fields.Many2one(
        'btp.lead.stage',
        string='Stage',
        group_expand='_read_group_stage_ids',
        default=lambda self: self._get_default_stage(),
        tracking=True,
        index=True,
        help='Current stage in the qualification workflow'
    )
    qualification_status = fields.Selection([
        ('field', 'Field'),
        ('targeting', 'Targeting'),
        ('contact', 'Contact'),
        ('decision', 'Decision'),
    ], string='Qualification Status', default='field', tracking=True)
    
    # ========== Qualification Details ==========
    budget = fields.Monetary(
        string='Estimated Budget',
        currency_field='currency_id',
        tracking=True,
        help='Estimated project budget'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    probability = fields.Float(
        string='Probability (%)',
        default=0.0,
        tracking=True,
        help='Probability of winning this lead (0-100%)'
    )
    expected_revenue = fields.Monetary(
        string='Expected Revenue',
        currency_field='currency_id',
        compute='_compute_expected_revenue',
        store=True,
        help='Expected revenue based on budget and probability'
    )
    competitor_ids = fields.Many2many(
        'res.partner',
        'btp_lead_competitor_rel',
        'lead_id',
        'competitor_id',
        string='Competitors',
        domain="[('is_company', '=', True)]",
        help='Known competitors for this project'
    )
    tender_deadline = fields.Date(
        string='Tender Deadline',
        tracking=True,
        help='Deadline for tender submission (DCE)'
    )
    project_start_date = fields.Date(
        string='Project Start Date',
        tracking=True,
        help='Expected project start date'
    )
    project_duration = fields.Integer(
        string='Project Duration (days)',
        help='Expected duration of the project in days'
    )
    
    # ========== Follow-up & Reminders ==========
    next_reminder_date = fields.Datetime(
        string='Next Reminder',
        tracking=True,
        index=True,
        help='Next scheduled reminder date (mandatory at each stage)'
    )
    last_reminder_date = fields.Datetime(
        string='Last Reminder',
        readonly=True,
        help='Date of the last reminder sent'
    )
    reminder_count = fields.Integer(
        string='Reminder Count',
        default=0,
        readonly=True,
        help='Number of reminders sent'
    )
    escalation_date = fields.Datetime(
        string='Escalation Date',
        readonly=True,
        help='Date when lead was escalated to management'
    )
    is_escalated = fields.Boolean(
        string='Escalated',
        default=False,
        tracking=True,
        help='Lead has been escalated to management'
    )
    escalation_reason = fields.Text(
        string='Escalation Reason',
        help='Reason for escalation'
    )
    
    # ========== Response Classification ==========
    response_status = fields.Selection([
        ('no_need_now', 'No Need Now'),
        ('later', 'Later'),
        ('immediate', 'Immediate'),
        ('not_interested', 'Not Interested'),
        ('lost', 'Lost'),
    ], string='Response Status', tracking=True)
    response_note = fields.Text(
        string='Response Note',
        help='Details about the prospect response'
    )
    
    # ========== Multi-Company Support ==========
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
        tracking=True
    )
    sharing_type = fields.Selection([
        ('exclusive', 'Exclusive'),
        ('shared', 'Shared'),
        ('global', 'Global'),
    ], string='Sharing Type', default='exclusive', tracking=True,
       help='How this lead is shared across companies')
    shared_company_ids = fields.Many2many(
        'res.company',
        'btp_lead_shared_company_rel',
        'lead_id',
        'company_id',
        string='Shared Companies',
        help='Companies with access to this lead (if shared)'
    )
    
    # ========== Anti-Duplicate ==========
    duplicate_ids = fields.Many2many(
        'btp.lead',
        'btp_lead_duplicate_rel',
        'lead_id',
        'duplicate_id',
        string='Potential Duplicates',
        help='Leads that might be duplicates'
    )
    is_duplicate = fields.Boolean(
        string='Is Duplicate',
        default=False,
        help='This lead is marked as a duplicate'
    )
    original_lead_id = fields.Many2one(
        'btp.lead',
        string='Original Lead',
        help='Original lead if this is a duplicate'
    )
    
    # ========== Conversion ==========
    converted = fields.Boolean(
        string='Converted',
        default=False,
        tracking=True,
        help='Lead has been converted to opportunity/quote'
    )
    converted_date = fields.Datetime(
        string='Converted Date',
        readonly=True,
        help='Date when lead was converted'
    )
    opportunity_id = fields.Many2one(
        'crm.lead',
        string='Opportunity',
        readonly=True,
        help='CRM opportunity created from this lead'
    )
    quote_id = fields.Many2one(
        'sale.order',
        string='Quote',
        readonly=True,
        help='Sale order/quote created from this lead'
    )
    can_be_converted = fields.Boolean(
        string='Can Be Converted',
        compute='_compute_can_be_converted',
        help='Whether this lead can be converted to an opportunity (must be in Qualified stage or later)'
    )
    
    @api.depends('stage_id', 'stage_id.sequence', 'converted')
    def _compute_can_be_converted(self):
        """Check if lead can be converted (must be in Qualified stage or later)"""
        for lead in self:
            if lead.converted:
                lead.can_be_converted = False
            elif lead.stage_id and (lead.stage_id.sequence or 0) >= 10:
                # Qualified stage has sequence 10, so any stage with sequence >= 10 is qualified
                lead.can_be_converted = True
            else:
                lead.can_be_converted = False
    
    # ========== Metadata ==========
    description = fields.Html(
        string='Description',
        help='Detailed description of the lead'
    )
    note = fields.Text(
        string='Internal Note',
        help='Internal notes (not visible to customer)'
    )
    tag_ids = fields.Many2many(
        'btp.lead.tag',
        string='Tags',
        help='Tags for categorization'
    )
    color = fields.Integer(string='Color', default=0)
    
    # ========== Statistics ==========
    email_count = fields.Integer(
        string='Email Count',
        compute='_compute_communication_stats',
        help='Number of emails'
    )
    call_count = fields.Integer(
        string='Call Count',
        compute='_compute_communication_stats',
        help='Number of calls'
    )
    meeting_count = fields.Integer(
        string='Meeting Count',
        compute='_compute_communication_stats',
        help='Number of meetings'
    )
    
    # ========== Computed Fields ==========
    @api.depends('budget', 'probability')
    def _compute_expected_revenue(self):
        for lead in self:
            lead.expected_revenue = (lead.budget or 0.0) * (lead.probability / 100.0)
    
    @api.depends('message_ids')
    def _compute_communication_stats(self):
        for lead in self:
            messages = lead.message_ids.filtered(lambda m: m.message_type in ['email', 'notification'])
            lead.email_count = len(messages.filtered(lambda m: m.message_type == 'email'))
            # Calls and meetings would come from activities
            activities = self.env['mail.activity'].search([
                ('res_id', '=', lead.id),
                ('res_model', '=', 'btp.lead')
            ])
            lead.call_count = len(activities.filtered(lambda a: a.activity_type_id.category == 'call'))
            lead.meeting_count = len(activities.filtered(lambda a: a.activity_type_id.category == 'meeting'))
    
    # ========== Defaults ==========
    @api.model
    def _get_default_stage(self):
        return self.env['btp.lead.stage'].search([('sequence', '=', 0)], limit=1)
    
    # ========== Constraints ==========
    @api.constrains('probability')
    def _check_probability(self):
        for lead in self:
            if lead.probability < 0 or lead.probability > 100:
                raise ValidationError(_('Probability must be between 0 and 100.'))
    
    @api.constrains('next_reminder_date')
    def _check_next_reminder(self):
        for lead in self:
            if lead.stage_id and lead.stage_id.require_reminder and not lead.next_reminder_date:
                raise ValidationError(_('Next reminder date is mandatory at this stage.'))
    
    # ========== Name Get ==========
    def name_get(self):
        result = []
        for lead in self:
            name = lead.name
            if lead.site_name:
                name = f"{name} - {lead.site_name}"
            result.append((lead.id, name))
        return result
    
    # ========== Stage Group Expand ==========
    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None):
        return stages.search([], order=order or 'sequence, id')
    
    # ========== Actions ==========
    def action_take_lead(self):
        """Claim an open lead"""
        if not self.is_open:
            raise UserError(_('This lead is not open for claiming.'))
        if self.user_id and self.user_id != self.env.user:
            raise UserError(_('This lead is already assigned to another user.'))
        
        self.write({
            'user_id': self.env.user.id,
            'is_open': False,
            'claimed_date': fields.Datetime.now(),
        })
        return True
    
    def action_assign(self, user_id=None, keep_open=False):
        """Assign lead to a user
        
        :param user_id: User to assign to (defaults to current user)
        :param keep_open: If True, keep lead as common open (visible to all)
        """
        if not user_id:
            user_id = self.env.user.id
        self.write({
            'user_id': user_id,
            'is_open': keep_open,
            'claimed_date': fields.Datetime.now() if not keep_open else False,
        })
        return True
    
    def action_convert_to_opportunity(self):
        """Convert lead to CRM opportunity
        
        Salespeople can convert leads assigned to them.
        Managers and Admins can convert any lead.
        Leads must be in "Qualified" stage or later to be converted.
        """
        self.ensure_one()
        if self.converted:
            raise UserError(_('This lead has already been converted.'))
        
        # Check if lead is in a qualified stage (sequence >= 10, which is "Qualified" stage)
        if not self.stage_id or (self.stage_id.sequence or 0) < 10:
            raise UserError(_('This lead cannot be converted yet. Please move it to "Qualified" stage or later before converting.'))
        
        # Security check: Salespeople can only convert leads assigned to them
        # Note: Leads can be both "open" (is_open=True) and assigned (user_id set)
        is_salesperson = self.env.user.has_group('btp_prospecting.group_btp_salesperson')
        is_manager_or_admin = (
            self.env.user.has_group('btp_prospecting.group_btp_manager') or
            self.env.user.has_group('btp_prospecting.group_btp_admin')
        )
        
        if is_salesperson and not is_manager_or_admin:
            # Salesperson can only convert leads assigned to them
            # Check if lead is assigned to current user
            if self.user_id and self.user_id == self.env.user:
                # Lead is assigned to current user - allow conversion
                pass
            elif self.is_open and not self.user_id:
                # Lead is open and unassigned - salesperson can't convert open leads
                raise UserError(_('You can only convert leads assigned to you. Please take the lead first.'))
            else:
                # Lead is assigned to someone else or not accessible
                raise UserError(_('You can only convert leads assigned to you.'))
        
        # Create CRM opportunity
        # Use sudo() to ensure opportunity creation works for all users
        # This is an internal operation, so using sudo() is appropriate
        opportunity = self.env['crm.lead'].sudo().create({
            'name': self.name,
            'type': 'opportunity',  # Explicitly set as opportunity
            'partner_id': self.partner_id.id if self.partner_id else False,
            'contact_name': self.contact_id.name if self.contact_id else self.partner_name,
            'email_from': self.partner_email,
            'phone': self.partner_phone,
            'user_id': self.user_id.id if self.user_id else False,
            'team_id': self.user_id.sale_team_id.id if self.user_id and self.user_id.sale_team_id else False,
            'expected_revenue': self.expected_revenue,
            'probability': self.probability,
            'description': self.description,
            'source_id': self._get_or_create_source(),
        })
        
        # Update lead - use sudo() to ensure write works
        # This is an internal operation, so using sudo() is appropriate
        self.sudo().write({
            'converted': True,
            'converted_date': fields.Datetime.now(),
            'opportunity_id': opportunity.id,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Opportunity'),
            'res_model': 'crm.lead',
            'res_id': opportunity.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def _get_or_create_source(self):
        """Get or create source for CRM
        
        Uses sudo() if needed to ensure salespeople can create sources.
        """
        if not self.origin:
            return False
        
        source_name = dict(self._fields['origin'].selection).get(self.origin, self.origin)
        # Try to find existing source
        source = self.env['utm.source'].search([('name', '=', source_name)], limit=1)
        if not source:
            # Create source - use sudo() if needed to ensure access
            try:
                source = self.env['utm.source'].create({'name': source_name})
            except Exception:
                # If creation fails due to access rights, try with sudo()
                source = self.env['utm.source'].sudo().create({'name': source_name})
        return source.id if source else False
    
    def action_set_reminder(self, days=0):
        """Set next reminder date"""
        self.ensure_one()
        if days == 0:
            # Default: today
            next_date = fields.Datetime.now()
        else:
            next_date = fields.Datetime.now() + timedelta(days=days)
        
        self.write({'next_reminder_date': next_date})
        return True
    
    def action_send_reminder(self):
        """Manually trigger reminder for this lead
        
        Salespeople can only send reminders for leads assigned to them.
        Managers and Admins can send reminders for any lead they can see.
        """
        self.ensure_one()
        
        if not self.user_id:
            raise UserError(_('This lead is not assigned to anyone. Please assign it to a user before sending a reminder.'))
        
        # Security check: Salespeople can only send reminders for their own leads
        is_salesperson = self.env.user.has_group('btp_prospecting.group_btp_salesperson')
        is_manager_or_admin = (
            self.env.user.has_group('btp_prospecting.group_btp_manager') or
            self.env.user.has_group('btp_prospecting.group_btp_admin')
        )
        
        if is_salesperson and not is_manager_or_admin:
            # Salesperson can only send reminders for leads assigned to them
            if self.user_id != self.env.user:
                raise UserError(_('You can only send reminders for leads assigned to you.'))
        
        # Send the reminder
        self._send_reminder()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Reminder Sent'),
                'message': _('Reminder has been sent to %s.') % self.user_id.name,
                'type': 'success',
            }
        }
    
    def action_check_duplicates(self):
        """Check for potential duplicates
        
        Salespeople can check duplicates, but will only see duplicates they have access to.
        Managers and Admins can see all duplicates.
        """
        self.ensure_one()
        # Use sudo() to find all duplicates regardless of access rights
        all_duplicates = self._find_duplicates()
        
        # Filter to only show duplicates the current user can access
        # Check access by trying to search for each duplicate with user's access rights
        visible_duplicates = self.env['btp.lead']
        accessible_ids = []
        
        for dup in all_duplicates:
            try:
                # Check if user can access this duplicate by searching for it
                accessible = self.env['btp.lead'].search([('id', '=', dup.id)], limit=1)
                if accessible:
                    visible_duplicates |= dup
                    accessible_ids.append(dup.id)
            except:
                # User doesn't have access to this duplicate
                pass
        
        # Only store duplicates the user can access (to avoid access rights errors)
        if accessible_ids:
            # Write using sudo() to bypass access rights, but only store accessible duplicates
            # This ensures salespeople can use the feature without access errors
            # We use sudo() on the record to bypass access checks on the Many2many field
            self.sudo().write({'duplicate_ids': [(6, 0, accessible_ids)]})
        
        if visible_duplicates:
            # Try to get the duplicate view, fallback to default list view if not found
            try:
                duplicate_view = self.env.ref('btp_prospecting.view_btp_lead_duplicate_tree', raise_if_not_found=False)
                view_id = duplicate_view.id if duplicate_view else False
            except:
                view_id = False
            
            return {
                'type': 'ir.actions.act_window',
                'name': _('Potential Duplicates'),
                'res_model': 'btp.lead',
                'domain': [('id', 'in', visible_duplicates.ids)],
                'view_mode': 'list,form',
                'views': [(view_id, 'list'), (False, 'form')] if view_id else [(False, 'list'), (False, 'form')],
                'target': 'new',
                'context': {'create': False},
            }
        elif all_duplicates:
            # Found duplicates but user can't see them
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Duplicates Found'),
                    'message': _('Found %d potential duplicate(s), but you don\'t have access to view them. Contact your manager for assistance.') % len(all_duplicates),
                    'type': 'warning',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Duplicates Found'),
                    'message': _('No potential duplicates found for this lead.'),
                    'type': 'success',
                }
            }
    
    def _find_duplicates(self):
        """Find potential duplicate leads
        
        Duplicate detection criteria (OR logic - matches if ANY criteria match):
        1. Same site_name (case-insensitive)
        2. Same partner_id (if both have partner)
        3. Same partner_name (if both have partner_name, case-insensitive)
        4. Similar site_address (first 50 chars, case-insensitive)
        5. Same lead name (case-insensitive) - if very similar names
        
        Uses sudo() to bypass record rules and find all potential duplicates,
        regardless of who can see them. This ensures comprehensive duplicate detection.
        """
        self.ensure_one()
        
        # Base domain: exclude current lead
        base_domain = [
            ('id', '!=', self.id),
        ]
        
        # Build OR conditions for duplicate detection
        or_conditions = []
        
        # 1. Check by site_name (most common identifier for BTP leads)
        if self.site_name:
            or_conditions.append(('site_name', 'ilike', self.site_name))
        
        # 2. Check by partner_id (if both leads have a partner)
        if self.partner_id:
            or_conditions.append(('partner_id', '=', self.partner_id.id))
        
        # 3. Check by partner_name (if both leads have partner_name but no partner_id)
        if self.partner_name and not self.partner_id:
            or_conditions.append(('partner_name', 'ilike', self.partner_name))
        
        # 4. Check by site_address (similar address - use first meaningful part)
        if self.site_address:
            address_clean = self.site_address.strip()
            # Extract first meaningful part (before comma or first 30 chars)
            if ',' in address_clean:
                address_search = address_clean.split(',')[0].strip()
            else:
                address_search = address_clean[:30].strip()
            
            if len(address_search) >= 5:  # Only if address is meaningful (reduced from 10)
                or_conditions.append(('site_address', 'ilike', '%' + address_search + '%'))
        
        # 5. Check by lead name (if names are very similar)
        if self.name:
            # Remove common suffixes/prefixes and check similarity
            name_clean = self.name.strip()
            if len(name_clean) >= 5:  # Only if name is meaningful
                or_conditions.append(('name', 'ilike', name_clean))
        
        # If no criteria to check, return empty
        if not or_conditions:
            return self.env['btp.lead']
        
        # Build final domain with OR logic
        # Odoo OR syntax: ['|', '|', condition1, condition2, condition3] means (condition1 OR condition2) OR condition3
        domain = base_domain.copy()
        
        if len(or_conditions) == 1:
            # Single condition: just add it
            domain.extend(or_conditions)
        else:
            # Multiple conditions: need OR operators
            # For n conditions, we need n-1 OR operators at the beginning
            # Format: ['|', '|', ..., condition1, condition2, ..., conditionN]
            or_operators = ['|'] * (len(or_conditions) - 1)
            domain.extend(or_operators)
            domain.extend(or_conditions)
        
        # Use sudo() to bypass record rules and find all duplicates
        duplicates = self.sudo().search(domain)
        return duplicates
    
    # ========== Override Create ==========
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Enforce non-sales leads as common open (bypass auto-assignment)
            if self.env.user.has_group('btp_prospecting.group_btp_non_sales'):
                vals['user_id'] = False
                vals['is_open'] = True
            else:
                # For salespeople: try auto-assignment when lead is not open and not assigned
                if not vals.get('user_id') and not vals.get('is_open'):
                    assigned = self._auto_assign_lead(vals)
                    if assigned:
                        vals['user_id'] = assigned['user_id'].id
                        vals['assignment_rule_id'] = assigned['rule_id'].id
                        vals['is_open'] = False
                    else:
                        # No rule matched: assign to creator to satisfy salesperson rule
                        if self.env.user.has_group('btp_prospecting.group_btp_salesperson'):
                            vals['user_id'] = self.env.user.id
                            vals['is_open'] = False
                # Note: is_open and user_id can both be True (assigned but still visible to all)

            if vals.get('user_id'):
                vals['last_assigned_user_id'] = vals['user_id']
                # Only set claimed_date if lead is not open
                if not vals.get('is_open', False):
                    vals['claimed_date'] = fields.Datetime.now()

            # Set default next reminder
            if 'next_reminder_date' not in vals:
                vals['next_reminder_date'] = fields.Datetime.now()
        
        leads = super(BtpLead, self).create(vals_list)
        for lead in leads:
            # Automatically detect duplicates on creation
            # Use sudo() to find all duplicates regardless of access rights
            duplicates = lead.sudo()._find_duplicates()
            if duplicates:
                # Filter to only store duplicates the current user can access
                accessible_ids = []
                all_duplicate_count = len(duplicates)
                
                for dup in duplicates:
                    try:
                        # Check if user can access this duplicate
                        accessible = self.env['btp.lead'].search([('id', '=', dup.id)], limit=1)
                        if accessible:
                            accessible_ids.append(dup.id)
                    except:
                        pass
                
                # Store accessible duplicates using sudo() to avoid access issues
                if accessible_ids:
                    lead.sudo().write({'duplicate_ids': [(6, 0, accessible_ids)]})
                
                # Add a note to the lead if duplicates were found
                if all_duplicate_count > 0:
                    accessible_count = len(accessible_ids)
                    if accessible_count > 0:
                        message = _('⚠️ <strong>Potential Duplicates Detected:</strong> %d duplicate lead(s) found during creation. Please review the "Duplicates" tab.') % accessible_count
                        if all_duplicate_count > accessible_count:
                            message += _('<br/>Note: %d additional duplicate(s) were found but you don\'t have access to view them.') % (all_duplicate_count - accessible_count)
                    else:
                        message = _('⚠️ <strong>Potential Duplicates Detected:</strong> %d duplicate lead(s) found during creation, but you don\'t have access to view them. Contact your manager for assistance.') % all_duplicate_count
                    
                    # Format message as HTML
                    lead.sudo().message_post(
                        body=Markup(message),
                        subject=_('Duplicate Detection'),
                    )

        return leads

    def write(self, vals):
        if self.env.context.get('btp_skip_open_sync'):
            return super().write(vals)

        # If stage requires reminder, ensure it's set
        if 'stage_id' in vals:
            stage = self.env['btp.lead.stage'].browse(vals['stage_id'])
            if stage.require_reminder and not vals.get('next_reminder_date'):
                vals = dict(vals)
                vals['next_reminder_date'] = fields.Datetime.now()

        # Store last_assigned_user_id when user_id is set
        if 'user_id' in vals and vals.get('user_id'):
            vals = dict(vals)
            vals['last_assigned_user_id'] = vals['user_id']
            # Only clear claimed_date if lead is being made not open
            if 'is_open' not in vals or not vals.get('is_open'):
                vals['claimed_date'] = fields.Datetime.now() if not vals.get('is_open', False) else False
        elif 'is_open' in vals and vals.get('is_open') and 'user_id' not in vals:
            # When making lead open without setting user_id, store current assignee
            for lead in self:
                if lead.user_id:
                    super(BtpLead, lead).with_context(btp_skip_open_sync=True).write({
                        'last_assigned_user_id': lead.user_id.id,
                    })

        # If a lead is explicitly set to not open and no user_id is provided, restore previous assignee
        if 'is_open' in vals and vals.get('is_open') is False and 'user_id' not in vals:
            result = True
            for lead in self:
                per_vals = dict(vals)
                per_vals['user_id'] = lead.last_assigned_user_id.id or self.env.user.id
                per_vals['last_assigned_user_id'] = per_vals['user_id']
                per_vals['claimed_date'] = fields.Datetime.now()
                result = super(BtpLead, lead).with_context(btp_skip_open_sync=True).write(per_vals)
            return result

        return super().write(vals)
    
    def _auto_assign_lead(self, vals):
        """Auto-assign lead based on assignment rules
        
        Uses sudo() to bypass access rights since salespeople don't need
        direct access to assignment rules - this is an internal system operation.
        """
        # Use sudo() to access assignment rules (salespeople can't read them directly)
        rules = self.env['btp.lead.assignment.rule'].sudo().search([
            ('active', '=', True),
            ('company_id', 'in', [False, self.env.company.id]),
        ], order='sequence')
        
        for rule in rules:
            if rule.match(vals):
                if rule.assignment_type == 'round_robin':
                    assigned_user = rule.assign_round_robin()
                else:
                    assigned_user = rule.user_id

                if assigned_user:
                    return {
                        'user_id': assigned_user,
                        'rule_id': rule,
                    }
        
        return False
    
    # ========== Override Write ==========
    # ========== Mail Thread Override ==========
    def _message_add_default_recipients(self):
        defaults = super(BtpLead, self)._message_add_default_recipients()
        for lead in self:
            partners = defaults[lead.id]['partners']
            if lead.partner_id:
                partners |= lead.partner_id
            if lead.contact_id:
                partners |= lead.contact_id
            defaults[lead.id]['partners'] = partners
        return defaults
    
    # ========== Cron Methods ==========
    @api.model
    def _cron_send_reminders(self):
        """Send reminders for leads that need follow-up (D0, +15, +30)"""
        now = fields.Datetime.now()
        
        # Find leads that need reminders
        leads = self.search([
            ('active', '=', True),
            ('converted', '=', False),
            ('next_reminder_date', '<=', now),
            ('next_reminder_date', '!=', False),
        ])
        
        for lead in leads:
            try:
                lead._send_reminder()
            except Exception as e:
                _logger.error(f"Error sending reminder for lead {lead.id}: {e}")
        
        return True
    
    def _send_reminder(self):
        """Send reminder for this lead"""
        self.ensure_one()
        
        if not self.user_id:
            return
        
        # Calculate days since last reminder or creation
        if self.last_reminder_date:
            days_since = (fields.Datetime.now() - self.last_reminder_date).days
        else:
            days_since = (fields.Datetime.now() - self.create_date).days
        
        # Determine reminder type
        if days_since == 0:
            reminder_type = 'D0'
        elif days_since == 15:
            reminder_type = '+15'
        elif days_since >= 30:
            reminder_type = '+30'
        else:
            reminder_type = 'custom'
        
        # Create activity/notification using activity_schedule method
        self.activity_schedule(
            act_type_xmlid='mail.mail_activity_data_todo',
            date_deadline=fields.Date.today(),
            summary=_('Lead Reminder: %s') % reminder_type,
            note=_('This lead requires follow-up. Next reminder was scheduled for %s.') % self.next_reminder_date,
            user_id=self.user_id.id,
        )
        
        # Send email notification
        template = self.env.ref('btp_prospecting.email_template_lead_reminder', raise_if_not_found=False)
        if template and self.user_id.email:
            template.send_mail(self.id, force_send=True)
        
        # Update reminder tracking
        self.write({
            'last_reminder_date': fields.Datetime.now(),
            'reminder_count': self.reminder_count + 1,
        })
        
        # Schedule next reminder based on current stage
        self._schedule_next_reminder()
    
    def _schedule_next_reminder(self):
        """Schedule next reminder based on stage and reminder count"""
        self.ensure_one()
        
        if self.reminder_count == 0:
            # D0: Today
            next_date = fields.Datetime.now()
        elif self.reminder_count == 1:
            # +15: 15 days from now
            next_date = fields.Datetime.now() + timedelta(days=15)
        elif self.reminder_count >= 2:
            # +30: 30 days from now
            next_date = fields.Datetime.now() + timedelta(days=30)
        else:
            next_date = fields.Datetime.now() + timedelta(days=30)
        
        self.write({'next_reminder_date': next_date})
    
    @api.model
    def _cron_escalate_leads(self):
        """Escalate leads that haven't been updated in 30+ days"""
        now = fields.Datetime.now()
        escalation_threshold = now - timedelta(days=30)
        
        # Find leads that need escalation
        leads = self.search([
            ('active', '=', True),
            ('converted', '=', False),
            ('is_escalated', '=', False),
            ('write_date', '<=', escalation_threshold),
        ])
        
        for lead in leads:
            try:
                lead._escalate_to_management()
            except Exception as e:
                _logger.error(f"Error escalating lead {lead.id}: {e}")
        
        return True
    
    def _escalate_to_management(self):
        """Escalate lead to management"""
        self.ensure_one()
        
        # Find manager (user's manager or team manager)
        manager = False
        if self.user_id and self.user_id.manager_id:
            manager = self.user_id.manager_id
        elif self.user_id and self.user_id.sale_team_id and self.user_id.sale_team_id.user_id:
            manager = self.user_id.sale_team_id.user_id
        
        if not manager:
            # Find any BTP manager
            manager = self.env['res.users'].search([
                ('groups_id', 'in', self.env.ref('btp_prospecting.group_btp_manager').ids)
            ], limit=1)
        
        if manager:
            # Create activity for manager using activity_schedule method
            self.activity_schedule(
                act_type_xmlid='mail.mail_activity_data_todo',
                date_deadline=fields.Date.today(),
                summary=_('Lead Escalation: Stalled Lead'),
                note=_('This lead has been stalled for 30+ days and requires management attention. '
                       'Consider reassigning or taking action.'),
                user_id=manager.id,
            )
            
            # Send email to manager
            template = self.env.ref('btp_prospecting.email_template_lead_escalation', raise_if_not_found=False)
            if template and manager.email:
                template.send_mail(self.id, force_send=True)
        
        self.write({
            'is_escalated': True,
            'escalation_date': fields.Datetime.now(),
            'escalation_reason': _('Lead stalled for 30+ days without update'),
        })
    
    @api.model
    def _cron_send_loop_reminders(self):
        """Send 6-month loop reminders for lost/end-of-site/unsuccessful leads"""
        now = fields.Datetime.now()
        six_months_ago = now - timedelta(days=180)
        
        # Find leads that need 6-month loop reminders
        # This includes: lost leads, end-of-site leads, unsuccessful leads
        leads = self.search([
            ('active', '=', True),
            ('stage_id.is_lost', '=', True),
            ('converted_date', '<=', six_months_ago),
            ('response_status', 'in', ['lost', 'not_interested', 'no_need_now']),
        ])
        
        for lead in leads:
            try:
                lead._send_loop_reminder()
            except Exception as e:
                _logger.error(f"Error sending loop reminder for lead {lead.id}: {e}")
        
        return True
    
    def _send_loop_reminder(self):
        """Send 6-month loop reminder"""
        self.ensure_one()
        
        if not self.user_id:
            return
        
        # Create activity using activity_schedule method
        self.activity_schedule(
            act_type_xmlid='mail.mail_activity_data_todo',
            date_deadline=fields.Date.today(),
            summary=_('6-Month Loop Reminder'),
            note=_('This lead was lost/unsuccessful 6 months ago. Consider re-contacting for new opportunities.'),
            user_id=self.user_id.id,
        )
        
        # Send email
        template = self.env.ref('btp_prospecting.email_template_lead_loop_reminder', raise_if_not_found=False)
        if template and self.user_id.email:
            template.send_mail(self.id, force_send=True)


class BtpLeadTag(models.Model):
    """Tags for lead categorization"""
    _name = 'btp.lead.tag'
    _description = 'BTP Lead Tag'
    
    name = fields.Char(string='Tag Name', required=True, translate=True)
    color = fields.Integer(string='Color', default=10)
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Tag name must be unique!'),
    ]

