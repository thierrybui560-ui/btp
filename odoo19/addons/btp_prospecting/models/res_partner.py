# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import re
from datetime import datetime, timedelta

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
    btp_subcontractor_site_ids = fields.One2many(
        'btp.company.site',
        'subcontractor_id',
        string='Subcontractor Sites',
        help='Sites where this partner is linked as subcontractor'
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

    # ========== Supplier/Subcontractor Fields ==========
    # Note: Temporarily commented out to allow server startup
    # These fields will be uncommented after module upgrade completes
    # Uncomment these fields after running: python3 odoo-bin -u btp_prospecting -d odoo_btp
    is_supplier = fields.Boolean(
        string='Is Supplier',
        default=False,
        tracking=True,
        help='This partner is a supplier'
    )
    is_subcontractor = fields.Boolean(
        string='Is Subcontractor',
        default=False,
        tracking=True,
        help='This partner is a subcontractor'
    )
    # Supplier/Subcontractor hierarchy (reuse company hierarchy fields)
    # btp_group_id, btp_subsidiary_id, btp_agency_id already exist for companies
    # For suppliers/subcontractors, we can attach to multiple agencies
    btp_supplier_agency_ids = fields.Many2many(
        'btp.company.agency',
        'btp_supplier_agency_rel',
        'supplier_id',
        'agency_id',
        string='Attached Agencies',
        help='Agencies this supplier/subcontractor is attached to'
    )
    # Supplier/Subcontractor documents (certificates, URSSAF, taxes, insurances)
    btp_supplier_document_ids = fields.One2many(
        'btp.supplier.document',
        'supplier_id',
        string='Supplier Documents',
        help='URSSAF certificates, taxes, insurances, paid vacations'
    )
    btp_supplier_document_count = fields.Integer(
        string='Documents Count',
        compute='_compute_supplier_document_count',
        store=True
    )
    btp_expired_documents_count = fields.Integer(
        string='Expired Documents',
        compute='_compute_supplier_document_count',
        store=True
    )
    btp_expiring_soon_documents_count = fields.Integer(
        string='Expiring Soon Documents',
        compute='_compute_supplier_document_count',
        store=True
    )
    btp_conformity_status = fields.Selection(
        [
            ('conform', 'Conform'),
            ('warning', 'Warning'),
            ('expired', 'Expired'),
            ('n_a', 'N/A'),
        ],
        string='Conformity Status',
        compute='_compute_btp_conformity_status',
        store=True,
        help='Document conformity status for suppliers/subcontractors (based on expired/expiring documents)'
    )
    btp_conformity_rate = fields.Float(
        string='Conformity Rate (%)',
        compute='_compute_btp_conformity_rate',
        store=True,
        help='Percentage of supplier/subcontractor documents that are conform (not expired or expiring soon)'
    )

    
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

    @api.depends('btp_supplier_document_ids', 'btp_supplier_document_ids.is_expired', 'btp_supplier_document_ids.expires_soon')
    def _compute_supplier_document_count(self):
        for record in self:
            record.btp_supplier_document_count = len(record.btp_supplier_document_ids)
            record.btp_expired_documents_count = len(record.btp_supplier_document_ids.filtered('is_expired'))
            record.btp_expiring_soon_documents_count = len(record.btp_supplier_document_ids.filtered('expires_soon'))

    @api.depends('btp_supplier_document_ids', 'btp_supplier_document_ids.is_expired', 'btp_supplier_document_ids.expires_soon')
    def _compute_btp_conformity_status(self):
        for partner in self:
            if not (partner.is_supplier or partner.is_subcontractor) or not partner.btp_supplier_document_ids:
                partner.btp_conformity_status = 'n_a'
            elif partner.btp_expired_documents_count and partner.btp_expired_documents_count > 0:
                partner.btp_conformity_status = 'expired'
            elif partner.btp_expiring_soon_documents_count and partner.btp_expiring_soon_documents_count > 0:
                partner.btp_conformity_status = 'warning'
            else:
                partner.btp_conformity_status = 'conform'

    @api.depends('btp_supplier_document_ids', 'btp_supplier_document_ids.is_expired', 'btp_supplier_document_ids.expires_soon')
    def _compute_btp_conformity_rate(self):
        for partner in self:
            total = len(partner.btp_supplier_document_ids)
            if not (partner.is_supplier or partner.is_subcontractor) or total == 0:
                partner.btp_conformity_rate = 0.0
            else:
                conform = total - len(partner.btp_supplier_document_ids.filtered(lambda d: d.is_expired or d.expires_soon))
                partner.btp_conformity_rate = round(100.0 * conform / total, 2) if total else 0.0

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
                # Keep Odoo standard salesperson (user_id) and BTP assignment aligned.
                if vals.get('user_id') and not vals.get('btp_assigned_salesperson_id'):
                    vals['btp_assigned_salesperson_id'] = vals['user_id']
                elif vals.get('btp_assigned_salesperson_id') and not vals.get('user_id'):
                    vals['user_id'] = vals['btp_assigned_salesperson_id']
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

            # Enrich suppliers/subcontractors from API if SIREN provided
            if vals.get('is_company') and (vals.get('is_supplier') or vals.get('is_subcontractor')) \
                    and vals.get('siren') and not vals.get('btp_api_enriched'):
                enriched_data = self._enrich_from_api(vals.get('siren'))
                if enriched_data:
                    vals.update(enriched_data)
                    vals['btp_api_enriched'] = True

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
                to_assign.sudo().write({
                    'btp_assigned_salesperson_id': self.env.user.id,
                    'user_id': self.env.user.id,
                })

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
                    managers = self.env['res.users']
                    if self.env.user.manager_id:
                        managers |= self.env.user.manager_id
                    if not managers:
                        managers |= self.env.ref(
                            'btp_prospecting.group_btp_manager'
                        ).users
                    for manager in managers:
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
                    self.env['btp.audit.log'].sudo().log(
                        'force_duplicate',
                        model_name='res.partner',
                        res_id=partner.id,
                        reason=_('Force duplicate contact: %s (ID %s); original %s (ID %s). N+1 notified.')
                        % (partner.display_name, partner.id, duplicate.display_name, duplicate.id),
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

        # Keep Odoo standard salesperson (user_id) and BTP assignment aligned for companies.
        # Without this, changes made from the standard Salesperson field are not tracked by governance.
        if ('user_id' in vals or 'btp_assigned_salesperson_id' in vals) and len(self) > 1:
            return all(record.write(vals) for record in self)
        if 'user_id' in vals or 'btp_assigned_salesperson_id' in vals or 'btp_contact_assigned_salesperson_id' in vals:
            is_company = bool(self and (self[0].is_company or self[0].company_type == 'company'))
            if is_company:
                vals = dict(vals)
                if 'user_id' in vals and 'btp_assigned_salesperson_id' not in vals:
                    vals['btp_assigned_salesperson_id'] = vals['user_id']
                elif 'btp_assigned_salesperson_id' in vals and 'user_id' not in vals:
                    vals['user_id'] = vals['btp_assigned_salesperson_id']
                # Defensive: if the contact-assignment field is edited on a company form,
                # treat it as a company salesperson change to keep governance logs consistent.
                if 'btp_contact_assigned_salesperson_id' in vals:
                    vals['btp_assigned_salesperson_id'] = vals['btp_contact_assigned_salesperson_id']
                    vals['user_id'] = vals['btp_contact_assigned_salesperson_id']

        # Snapshot old salesperson for companies/contacts before write (for reattribution after write)
        reattribution_candidates = []  # (partner_id, old_user_id, is_company)
        for partner in self:
            is_company = getattr(partner, 'is_company', False) or getattr(partner, 'company_type', None) == 'company'
            if is_company and ('btp_assigned_salesperson_id' in vals or 'user_id' in vals or 'btp_contact_assigned_salesperson_id' in vals):
                old_id = (
                    partner.btp_assigned_salesperson_id.id
                    if partner.btp_assigned_salesperson_id
                    else (partner.user_id.id if partner.user_id else None)
                )
                reattribution_candidates.append((partner.id, old_id, True))
            if not is_company and 'btp_contact_assigned_salesperson_id' in vals:
                old_id = partner.btp_contact_assigned_salesperson_id.id if partner.btp_contact_assigned_salesperson_id else None
                reattribution_candidates.append((partner.id, old_id, False))

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

        # Create reattribution and audit log when salesperson actually changed (after write)
        if reattribution_candidates:
            _logger.info(
                'BTP reattribution check: %s candidate(s) after write',
                len(reattribution_candidates),
            )
            reason = (self.env.context.get('btp_reattribution_reason') or '').strip()
            AuditLog = self.env['btp.audit.log'].sudo()
            User = self.env['res.users']
            created_reattributions = []
            for partner_id, old_user_id, is_company in reattribution_candidates:
                partner = self.browse(partner_id)
                if not partner.exists():
                    continue
                if is_company:
                    new_user = partner.btp_assigned_salesperson_id or partner.user_id
                else:
                    new_user = partner.btp_contact_assigned_salesperson_id
                new_user_id = new_user.id if new_user else None
                if old_user_id == new_user_id:
                    _logger.info(
                        'BTP reattribution skip: partner %s unchanged (old=%s new=%s)',
                        partner_id, old_user_id, new_user_id,
                    )
                    continue
                old_user = User.browse(old_user_id) if old_user_id else self.env['res.users']
                self.env['btp.company.reattribution'].sudo().create({
                    'partner_id': partner_id,
                    'old_user_id': old_user_id or False,
                    'new_user_id': new_user.id if new_user else False,
                    'changed_by_id': self.env.user.id,
                    'reason': reason or _('Manual reattribution from partner form.'),
                })
                created_reattributions.append(partner.display_name or str(partner_id))
                reason_text = _('Client reattribution: %s → %s. %s') % (
                    old_user.name if old_user else _('Unassigned'),
                    new_user.name if new_user else _('Unassigned'),
                    reason or _('No reason provided'),
                )
                AuditLog.create({
                    'user_id': self.env.user.id,
                    'action': 'reattribution',
                    'model_name': 'res.partner',
                    'res_id': partner_id,
                    'reason': reason_text,
                })

            # Optional UI feedback for manual changes from form/list view.
            # This complements governance logs and helps users confirm action happened.
            if created_reattributions and not self.env.context.get('btp_disable_reattribution_notification'):
                if len(created_reattributions) == 1:
                    message = _('Reattribution logged for %s.') % created_reattributions[0]
                else:
                    message = _('Reattribution logged for %s records.') % len(created_reattributions)
                try:
                    # Prefer the standard user notification API when available.
                    self.env.user.notify_success(message)
                except Exception:
                    # Fallback via bus for environments where notify_success is unavailable.
                    try:
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'simple_notification',
                            {
                                'title': _('Governance'),
                                'message': message,
                                'sticky': False,
                                'warning': False,
                            },
                        )
                    except Exception:
                        _logger.debug('Reattribution notification could not be sent to UI.', exc_info=True)

        if not self.env.context.get('skip_duplicate_recompute'):
            self._recompute_contact_duplicate_flags()

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

    def _btp_required_subcontractor_document_types(self):
        """Central list of mandatory subcontractor documents for compliance checks."""
        return {'urssaf', 'taxes', 'insurance', 'paid_vacations'}

    def _btp_get_subcontractor_document_issues(self):
        """Return missing/expired document issues for each subcontractor record.

        Result format:
        {
            partner_id: {
                'missing': set([...]),
                'expired': recordset(btp.supplier.document),
            }
        }
        """
        issues = {}
        required_types = self._btp_required_subcontractor_document_types()
        for partner in self:
            if not partner.is_subcontractor:
                continue
            docs = partner.btp_supplier_document_ids.filtered('active')
            present_types = set(docs.mapped('document_type'))
            missing = required_types - present_types
            expired = docs.filtered('is_expired')
            issues[partner.id] = {
                'missing': missing,
                'expired': expired,
            }
        return issues

    def _btp_validate_subcontractor_documents_or_raise(self):
        """Raise a business error when subcontractor docs are invalid and blocking is enabled."""
        block_enabled = self.env['ir.config_parameter'].sudo().get_param(
            'btp_prospecting.btp_subcontractor_blocking_enabled',
            'False',
        ) == 'True'
        if not block_enabled:
            return
        issues = self._btp_get_subcontractor_document_issues()
        error_lines = []
        for partner in self.filtered('is_subcontractor'):
            issue = issues.get(partner.id, {})
            missing = issue.get('missing', set())
            expired = issue.get('expired', self.env['btp.supplier.document'])
            if not missing and not expired:
                continue
            details = []
            if missing:
                labels = dict(self.env['btp.supplier.document']._fields['document_type'].selection)
                details.append(_('missing: %s') % ', '.join(sorted(labels.get(m, m) for m in missing)))
            if expired:
                details.append(
                    _('expired: %s') % ', '.join(sorted(expired.mapped('name')))
                )
            error_lines.append('- %s (%s)' % (partner.display_name, '; '.join(details)))
        if error_lines:
            raise ValidationError(
                _('Cannot proceed because subcontractor compliance documents are invalid:\n%s')
                % '\n'.join(error_lines)
            )
    
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

    # Module 15 — System Governance: automatic reattribution of inactive clients
    @api.model
    def _cron_reattribute_inactive_clients(self):
        """Reassign companies with no activity for N days to the salesperson's manager."""
        ICP = self.env['ir.config_parameter'].sudo()
        if not ICP.get_param('btp_prospecting.btp_automatic_reattribution_enabled', 'False') == 'True':
            return 0
        try:
            days = int(ICP.get_param('btp_prospecting.btp_reattribution_inactive_days', 30))
        except (TypeError, ValueError):
            days = 30
        threshold = datetime.now() - timedelta(days=days)
        threshold_str = threshold.strftime('%Y-%m-%d %H:%M:%S')
        domain = [
            ('is_company', '=', True),
            ('btp_assigned_salesperson_id', '!=', False),
            ('write_date', '<', threshold_str),
        ]
        partners = self.sudo().search(domain)
        reattributed = 0
        for partner in partners:
            user = partner.btp_assigned_salesperson_id
            if not user.manager_id:
                continue
            partner.with_context(
                btp_reattribution_reason=_('Automatic reattribution: no activity for %s days.') % days,
            ).sudo().write({'btp_assigned_salesperson_id': user.manager_id.id})
            reattributed += 1
        if reattributed:
            _logger.info('BTP automatic reattribution: %s client(s) reattributed to manager.', reattributed)
        return reattributed

