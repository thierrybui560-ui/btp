# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import re

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Extend res.partner for BTP Company and Contact management"""
    _inherit = 'res.partner'

    # ========== Company Fields (is_company = True) ==========
    siren = fields.Char(
        string='SIREN',
        size=9,
        tracking=True,
        help='9-digit SIREN number (legal identifier for companies)'
    )
    siret = fields.Char(
        string='SIRET',
        size=14,
        tracking=True,
        help='14-digit SIRET number (legal identifier for agencies/sites)'
    )
    naf_code = fields.Char(
        string='NAF Code',
        size=5,
        tracking=True,
        help='French NAF code (activity code)'
    )
    legal_form = fields.Char(
        string='Legal Form',
        tracking=True,
        help='Legal form (e.g., SARL, SA, SAS)'
    )
    capital = fields.Float(
        string='Capital',
        tracking=True,
        help='Company capital in EUR'
    )
    
    # Company Hierarchy
    btp_group_id = fields.Many2one(
        'btp.company.group',
        string='Group',
        tracking=True,
        help='Company group (top level)'
    )
    btp_subsidiary_id = fields.Many2one(
        'btp.company.subsidiary',
        string='Subsidiary',
        tracking=True,
        help='Company subsidiary (second level)'
    )
    btp_agency_id = fields.Many2one(
        'btp.company.agency',
        string='Agency',
        tracking=True,
        help='Company agency (third level)'
    )
    
    # Multi-company sharing
    btp_shared_company_ids = fields.Many2many(
        'res.company',
        'btp_partner_company_rel',
        'partner_id',
        'company_id',
        string='Shared Companies',
        help='Companies in the group that share this client'
    )
    
    # Company status
    btp_is_prospect = fields.Boolean(
        string='Is Prospect',
        default=True,
        tracking=True,
        help='Is this a prospect (not yet a client)?'
    )
    btp_is_client = fields.Boolean(
        string='Is Client',
        compute='_compute_client_status',
        store=True,
        help='Is this an active client?'
    )
    
    # Company assignment
    btp_assigned_salesperson_id = fields.Many2one(
        'res.users',
        string='Assigned Salesperson',
        tracking=True,
        help='Salesperson assigned to this company'
    )

    btp_address_ids = fields.One2many(
        'btp.company.address',
        'partner_id',
        string='Addresses'
    )
    btp_site_ids = fields.One2many(
        'btp.company.site',
        'company_id',
        string='Sites'
    )
    btp_commercial_condition_ids = fields.One2many(
        'btp.company.commercial.condition',
        'partner_id',
        string='Commercial Conditions'
    )
    btp_contact_count = fields.Integer(
        string='Contact Count',
        compute='_compute_contact_count',
        store=False
    )
    btp_reattribution_ids = fields.One2many(
        'btp.company.reattribution',
        'partner_id',
        string='Reattribution History'
    )
    
    # ========== Contact Fields (is_company = False) ==========
    mobile = fields.Char(
        string='Mobile',
        tracking=True,
        help='Mobile phone number'
    )
    # Contact assignment
    btp_contact_assigned_salesperson_id = fields.Many2one(
        'res.users',
        string='Assigned Salesperson',
        tracking=True,
        help='Salesperson assigned to this contact'
    )
    btp_force_duplicate = fields.Boolean(
        string='Force Duplicate',
        default=False,
        help='Force creation of a duplicate contact (manager will be notified if email/phone match).'
    )
    
    # Career history
    btp_career_history_ids = fields.One2many(
        'btp.contact.career',
        'contact_id',
        string='Career History',
        help='Career history across different companies'
    )
    btp_current_company_id = fields.Many2one(
        'res.partner',
        string='Current Company',
        compute='_compute_current_company',
        store=True,
        domain="[('is_company', '=', True)]",
        help='Contact\'s current company (from career history)'
    )
    
    # Duplicate detection flags
    btp_duplicate_warning = fields.Boolean(
        string='Duplicate Warning',
        default=False,
        help='Warning flag for potential duplicates'
    )
    btp_duplicate_message = fields.Text(
        string='Duplicate Message',
        help='Message explaining potential duplicate'
    )
    
    # API enrichment
    btp_api_enriched = fields.Boolean(
        string='API Enriched',
        default=False,
        help='Was this company enriched from external API?'
    )
    btp_api_source = fields.Selection([
        ('insee', 'INSEE'),
        ('pappers', 'Pappers'),
        ('infogreffe', 'Infogreffe'),
        ('manual', 'Manual Entry'),
    ], string='Data Source', default='manual')

    
    @api.depends('btp_career_history_ids', 'btp_career_history_ids.is_current', 'btp_career_history_ids.company_id', 'btp_career_history_ids.end_date', 'parent_id')
    def _compute_current_company(self):
        """Compute current company from career history"""
        for partner in self:
            if partner.is_company:
                partner.btp_current_company_id = False
            else:
                # Get current career (where is_current=True and end_date is empty)
                try:
                    current_career = partner.btp_career_history_ids.filtered(lambda c: c.is_current and not c.end_date)
                    if current_career:
                        partner.btp_current_company_id = current_career[0].company_id
                    elif partner.parent_id:
                        # Fallback to parent company when career history is missing
                        partner.btp_current_company_id = partner.parent_id
                    else:
                        partner.btp_current_company_id = False
                except Exception:
                    # Handle case where career history might not be loaded yet
                    partner.btp_current_company_id = False
    
    @api.depends('btp_is_prospect', 'sale_order_count')
    def _compute_client_status(self):
        """Compute if partner is a client (has orders)"""
        for partner in self:
            # Check if partner has sale orders (if sale module is installed)
            has_orders = False
            if hasattr(partner, 'sale_order_count'):
                has_orders = partner.sale_order_count > 0
            partner.btp_is_client = not partner.btp_is_prospect and has_orders

    def _compute_contact_count(self):
        for partner in self:
            if partner.is_company:
                partner.btp_contact_count = self.env['res.partner'].sudo().search_count([
                    ('parent_id', '=', partner.id),
                    ('is_company', '=', False)
                ])
            else:
                partner.btp_contact_count = 0

    @api.onchange('name', 'email', 'phone', 'mobile')
    def _onchange_contact_duplicate_warning(self):
        """Show duplicate warning before save so user can force duplicate."""
        for partner in self:
            if partner.is_company:
                partner.btp_duplicate_warning = False
                partner.btp_duplicate_message = False
                continue
            duplicate = partner._check_contact_duplicate(
                partner.name,
                partner.email,
                partner.phone,
                partner.mobile,
            )
            if duplicate and duplicate.id != partner.id:
                assigned_to = duplicate.btp_contact_assigned_salesperson_id.name if duplicate.btp_contact_assigned_salesperson_id else _('Unassigned')
                partner.btp_duplicate_warning = True
                partner.btp_duplicate_message = _(
                    'Potential duplicate: This contact already exists (assigned to %s).\n'
                    'If email and phone are identical, an alert will be sent to management.'
                ) % assigned_to
            else:
                partner.btp_duplicate_warning = False
                partner.btp_duplicate_message = False
    
    @api.constrains('siren')
    def _check_siren(self):
        """Validate SIREN format (9 digits)"""
        for partner in self:
            if partner.siren and partner.is_company:
                if not re.match(r'^\d{9}$', partner.siren):
                    raise ValidationError(_('SIREN must be exactly 9 digits.'))
                duplicate = self.sudo().search([
                    ('id', '!=', partner.id),
                    ('is_company', '=', True),
                    ('siren', '=', partner.siren),
                ], limit=1)
                if duplicate:
                    raise ValidationError(_('SIREN must be unique for companies.'))
    
    @api.constrains('siret')
    def _check_siret(self):
        """Validate SIRET format (14 digits)"""
        for partner in self:
            if partner.siret and partner.is_company:
                if not re.match(r'^\d{14}$', partner.siret):
                    raise ValidationError(_('SIRET must be exactly 14 digits.'))
                # SIRET should start with SIREN
                if partner.siren and not partner.siret.startswith(partner.siren):
                    raise ValidationError(_('SIRET must start with the SIREN number.'))
                duplicate = self.sudo().search([
                    ('id', '!=', partner.id),
                    ('is_company', '=', True),
                    ('siret', '=', partner.siret),
                ], limit=1)
                if duplicate:
                    raise ValidationError(_('SIRET must be unique for companies.'))
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to check for duplicates and enrich from API"""
        notify_candidates = []

        for vals in vals_list:
            # Ensure client companies are not restricted to a single company
            # Only clear company_id for companies, not contacts
            if vals.get('is_company') or vals.get('company_type') == 'company':
                vals['company_id'] = False
            # Default assignment to creator if not provided
            if (vals.get('is_company') or vals.get('company_type') == 'company') and not vals.get('btp_assigned_salesperson_id'):
                # Assign only for salespeople; managers/admins can assign manually
                if self.env.user.has_group('btp_prospecting.group_btp_salesperson'):
                    vals['btp_assigned_salesperson_id'] = self.env.user.id
            if not vals.get('is_company') and not vals.get('btp_contact_assigned_salesperson_id'):
                vals['btp_contact_assigned_salesperson_id'] = self.env.user.id
            # If contact has a typed company name but no parent_id, link/create it
            if not vals.get('is_company') and not vals.get('parent_id') and vals.get('company_name'):
                company = self.env['res.partner'].sudo().search([
                    ('is_company', '=', True),
                    ('name', '=', vals['company_name']),
                ], limit=1)
                if not company:
                    company = self.env['res.partner'].sudo().create({
                        'name': vals['company_name'],
                        'company_type': 'company',
                        'is_company': True,
                    })
                vals['parent_id'] = company.id
                vals['company_name'] = False

            # Check for company duplicates (SIREN/SIRET)
            if vals.get('is_company') and (vals.get('siren') or vals.get('siret')):
                duplicate = self._check_company_duplicate(vals.get('siren'), vals.get('siret'))
                if duplicate:
                    raise UserError(_(
                        'Company already exists with SIREN/SIRET: %s\n'
                        'See: %s'
                    ) % (vals.get('siren') or vals.get('siret'), duplicate.name))

            # Check for contact duplicates
            if not vals.get('is_company'):
                incoming_phone = vals.get('phone')
                incoming_mobile = vals.get('mobile')
                
                duplicate = self._check_contact_duplicate(
                    vals.get('name'),
                    vals.get('email'),
                    incoming_phone,
                    incoming_mobile
                )
                if duplicate:
                    # Block exact duplicates unless forced
                    same_email = vals.get('email') and duplicate.email and vals.get('email') == duplicate.email
                    # Get existing phone/mobile safely
                    existing_phone = duplicate.phone
                    existing_mobile = duplicate.mobile
                    same_phone = incoming_phone and existing_phone and incoming_phone == existing_phone
                    same_mobile = incoming_mobile and existing_mobile and incoming_mobile == existing_mobile
                    if (same_email or same_phone or same_mobile) and not vals.get('btp_force_duplicate'):
                        raise UserError(_(
                            'This contact already exists (assigned to %s). '
                            'Email/phone must be different to create a homonym. '
                            'If you must create it anyway, enable "Force Duplicate".'
                        ) % (duplicate.btp_contact_assigned_salesperson_id.name or _('Unassigned')))

                    # Set warning but allow creation (user can proceed)
                    vals['btp_duplicate_warning'] = True
                    assigned_to = duplicate.btp_contact_assigned_salesperson_id.name if duplicate.btp_contact_assigned_salesperson_id else _('Unassigned')
                    vals['btp_duplicate_message'] = _(
                        'Potential duplicate: This contact already exists (assigned to %s).\n'
                        'If email and phone are identical, an alert will be sent to management.'
                    ) % assigned_to

            # Enrich company from API if SIREN provided
            if vals.get('is_company') and vals.get('siren') and not vals.get('btp_api_enriched'):
                enriched_data = self._enrich_from_api(vals.get('siren'))
                if enriched_data:
                    vals.update(enriched_data)
                    vals['btp_api_enriched'] = True

            if vals.get('btp_force_duplicate'):
                notify_candidates.append(vals)

        partners = super(ResPartner, self).create(vals_list)

        partners._recompute_contact_duplicate_flags()

        # Safety: ensure assignment for companies created by salespeople
        if self.env.user.has_group('btp_prospecting.group_btp_salesperson'):
            to_assign = partners.filtered(
                lambda p: p.is_company
                and p.create_uid.id == self.env.user.id
                and not p.btp_assigned_salesperson_id
            )
            if to_assign:
                to_assign.sudo().write({'btp_assigned_salesperson_id': self.env.user.id})

        # Create initial career history for new contacts with a company
        for partner, vals in zip(partners, vals_list):
            if not partner.is_company:
                company_id = vals.get('parent_id') or partner.parent_id.id
                if company_id and not partner.btp_career_history_ids:
                    self.env['btp.contact.career'].sudo().create({
                        'contact_id': partner.id,
                        'company_id': company_id,
                        'job_title': vals.get('function') or partner.function or _('Unknown'),
                        'start_date': fields.Date.today(),
                        'is_current': True,
                    })

        # Notify manager if duplicate was forced with identical coordinates
        for partner in partners.filtered(lambda p: not p.is_company and p.btp_force_duplicate):
            partner_phone = partner.phone
            partner_mobile = partner.mobile
            
            duplicate = partner._check_contact_duplicate(
                partner.name,
                partner.email,
                partner_phone,
                partner_mobile
            )
            if duplicate and duplicate.id != partner.id:
                same_email = partner.email and duplicate.email and partner.email == duplicate.email
                incoming_phone = partner_phone
                incoming_mobile = partner_mobile
                existing_phone = duplicate.phone
                existing_mobile = duplicate.mobile
                same_phone = incoming_phone and existing_phone and incoming_phone == existing_phone
                same_mobile = incoming_mobile and existing_mobile and incoming_mobile == existing_mobile
                if same_email or same_phone or same_mobile:
                    manager = self.env.user.manager_id
                    if manager:
                        partner.activity_schedule(
                            'mail.mail_activity_data_todo',
                            user_id=manager.id,
                            summary=_('Duplicate contact created'),
                            note=_(
                                'A contact duplicate was forced with identical email/phone.\n'
                                'Original: %s (ID %s)\n'
                                'New: %s (ID %s)'
                            ) % (duplicate.display_name, duplicate.id, partner.display_name, partner.id),
                        )
        return partners

    def _recompute_contact_duplicate_flags(self):
        """Clear duplicate flags when no duplicate exists for current values."""
        for partner in self.filtered(lambda p: not p.is_company):
            duplicate = partner._check_contact_duplicate(
                partner.name,
                partner.email,
                partner.phone,
                partner.mobile,
            )
            if not duplicate or duplicate.id == partner.id:
                if partner.btp_duplicate_warning or partner.btp_duplicate_message:
                    partner.sudo().with_context(skip_duplicate_recompute=True).write({
                        'btp_duplicate_warning': False,
                        'btp_duplicate_message': False,
                    })
    
    def write(self, vals):
        """Override write to check duplicates and handle company changes"""
        if self.env.context.get('skip_career_update'):
            return super(ResPartner, self).write(vals)

        # Capture reattribution changes
        reassignments = []
        for partner in self:
            if partner.is_company and 'btp_assigned_salesperson_id' in vals:
                old_user = partner.btp_assigned_salesperson_id
                new_user = self.env['res.users'].browse(vals.get('btp_assigned_salesperson_id')) if vals.get('btp_assigned_salesperson_id') else False
                if old_user != new_user:
                    reassignments.append((partner, old_user, new_user))
            if not partner.is_company and 'btp_contact_assigned_salesperson_id' in vals:
                old_user = partner.btp_contact_assigned_salesperson_id
                new_user = self.env['res.users'].browse(vals.get('btp_contact_assigned_salesperson_id')) if vals.get('btp_contact_assigned_salesperson_id') else False
                if old_user != new_user:
                    reassignments.append((partner, old_user, new_user))
        # Handle contact company change (career history update)
        # Note: parent_id is the contact's company in res.partner
        for record in self:
            if not record.is_company and vals.get('parent_id'):
                # Only update if company actually changed
                current_company_id = record.parent_id.id if record.parent_id else False
                new_company_id = vals.get('parent_id')
                if current_company_id != new_company_id:
                    record._update_career_on_company_change(new_company_id, vals.get('function'))
        
        result = super(ResPartner, self).write(vals)

        if reassignments:
            for partner, old_user, new_user in reassignments:
                self.env['btp.company.reattribution'].sudo().create({
                    'partner_id': partner.id,
                    'old_user_id': old_user.id if old_user else False,
                    'new_user_id': new_user.id if new_user else False,
                    'changed_by_id': self.env.user.id,
                })

        if not self.env.context.get('skip_duplicate_recompute'):
            partners._recompute_contact_duplicate_flags()

        return result
    
    def _check_company_duplicate(self, siren=None, siret=None):
        """Check if company with same SIREN/SIRET already exists"""
        domain = [('is_company', '=', True), ('active', 'in', [True, False])]
        if siren:
            domain.append(('siren', '=', siren))
        elif siret:
            domain.append(('siret', '=', siret))
        else:
            return False
        
        return self.sudo().search(domain, limit=1)
    
    def _check_contact_duplicate(self, name=None, email=None, phone=None, mobile=None):
        """Check if contact with same name/email/phone/mobile already exists"""
        domain = [('is_company', '=', False), ('active', 'in', [True, False])]
        conditions = []
        
        if name:
            conditions.append([('name', '=', name)])
        
        if email:
            conditions.append([('email', '=', email)])
        
        if phone:
            conditions.append([('phone', '=', phone)])

        if mobile:
            conditions.append([('mobile', '=', mobile)])
        
        if not conditions:
            return False
        
        # Build OR domain
        or_domain = ['|'] * (len(conditions) - 1) + [item for sublist in conditions for item in sublist]
        domain = domain + or_domain
        
        return self.sudo().search(domain, limit=1)

    def _update_career_on_company_change(self, new_company_id, new_function=None):
        """Update career history when contact changes company"""
        for contact in self:
            if contact.is_company:
                continue  # Skip companies
            
            # End current career
            current_career = contact.btp_career_history_ids.filtered(lambda c: c.is_current and not c.end_date)
            if current_career:
                current_career.sudo().write({'end_date': fields.Date.today()})
            
            # Create new career entry if company provided
            if new_company_id:
                # Check if company is valid
                company = self.env['res.partner'].browse(new_company_id)
                if company.exists() and company.is_company:
                    self.env['btp.contact.career'].sudo().create({
                        'contact_id': contact.id,
                        'company_id': new_company_id,
                        'job_title': new_function or contact.function or _('Unknown'),
                        'start_date': fields.Date.today(),
                    })
    
    def _enrich_from_api(self, siren):
        """Enrich company data from external API (INSEE/Pappers)"""
        api_service = self.env['btp.company.api.service']
        enriched_data, source = api_service.enrich_company(siren)
        
        if enriched_data:
            enriched_data['btp_api_source'] = source
            return enriched_data
        
        return {}
    
    def action_enrich_from_api(self):
        """Manual action to enrich company from API"""
        if not self.is_company or not self.siren:
            raise UserError(_('Only companies with SIREN can be enriched from API.'))
        
        enriched_data = self._enrich_from_api(self.siren)
        if enriched_data:
            self.write(enriched_data)
            self.btp_api_enriched = True
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Company data enriched from API.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Warning'),
                    'message': _('No data found for SIREN: %s') % self.siren,
                    'type': 'warning',
                    'sticky': False,
                }
            }

