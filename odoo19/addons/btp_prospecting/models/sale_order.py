# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """Extend sale.order for BTP Quotes"""
    _inherit = 'sale.order'

    # ========== Quote Numbering ==========
    btp_quote_number = fields.Char(
        string='Quote Number',
        copy=False,
        readonly=True,
        index=True,
        help='Quote number in format YYYYMMNNN (e.g., 202501001)'
    )
    btp_revision_index = fields.Char(
        string='Revision',
        size=1,
        copy=False,
        readonly=True,
        help='Revision letter (A, B, C...) for modified quotes after sending'
    )
    btp_is_revision = fields.Boolean(
        string='Is Revision',
        compute='_compute_is_revision',
        store=True,
        help='This quote is a revision of a previously sent quote'
    )
    btp_original_quote_id = fields.Many2one(
        'sale.order',
        string='Original Quote',
        copy=False,
        help='Original quote if this is a revision'
    )
    btp_revision_ids = fields.One2many(
        'sale.order',
        'btp_original_quote_id',
        string='Revisions',
        help='All revisions of this quote'
    )

    # ========== Quote Structure ==========
    btp_lot_ids = fields.One2many(
        'btp.quote.lot',
        'quote_id',
        string='Lots',
        help='Quote lots (hierarchical structure)'
    )
    btp_lot_count = fields.Integer(
        string='Lots Count',
        compute='_compute_lot_count',
        store=True
    )

    # ========== Quote Status & Workflow ==========
    btp_quote_status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
        ('expired', 'Expired'),
    ], string='Quote Status',
        default='draft',
        tracking=True,
        help='Status of the quote'
    )
    btp_sent_date = fields.Datetime(
        string='Sent Date',
        copy=False,
        help='Date when the quote was sent to the client'
    )
    btp_next_followup_date = fields.Date(
        string='Next Follow-up Date',
        help='Next follow-up date (for reminders)'
    )
    btp_is_locked = fields.Boolean(
        string='Is Locked',
        compute='_compute_is_locked',
        store=True,
        help='Quote is locked (sent) and cannot be modified'
    )

    # ========== Totals ==========
    btp_total_cost = fields.Float(
        string='Total Cost',
        digits='Product Price',
        compute='_compute_btp_totals',
        store=True,
        help='Total cost of all items (articles + labor)'
    )
    btp_total_margin = fields.Float(
        string='Total Margin',
        digits='Product Price',
        compute='_compute_btp_totals',
        store=True,
        help='Total margin (amount_total - total_cost)'
    )
    btp_margin_percent = fields.Float(
        string='Margin %',
        digits=(12, 2),
        compute='_compute_btp_totals',
        store=True,
        help='Margin percentage'
    )

    # ========== Quote Analysis Fields ==========
    btp_days_to_send = fields.Integer(
        string='Days to Send',
        compute='_compute_days_to_send',
        store=True,
        help='Number of days between quote creation and sending'
    )
    btp_is_converted = fields.Boolean(
        string='Is Converted to Order',
        compute='_compute_is_converted',
        store=True,
        help='Quote has been converted to a sale order'
    )
    btp_site_id = fields.Many2one(
        'project.project',
        string='Site',
        copy=False,
        help='Site created from this accepted quote/order'
    )
    # Module 13 — Multi-companies: mark when document relates to shared client
    btp_is_shared = fields.Boolean(
        string='Shared Client',
        compute='_compute_btp_is_shared',
        store=True,
        help='True when the client (partner) is shared with other companies.'
    )

    @api.depends('partner_id', 'partner_id.btp_shared_company_ids')
    def _compute_btp_is_shared(self):
        for order in self:
            order.btp_is_shared = bool(
                order.partner_id
                and order.partner_id.btp_shared_company_ids
            )

    @api.depends('btp_lot_ids')
    def _compute_lot_count(self):
        for record in self:
            record.btp_lot_count = len(record.btp_lot_ids)

    @api.depends('btp_revision_index')
    def _compute_is_revision(self):
        for record in self:
            record.btp_is_revision = bool(record.btp_revision_index)

    @api.depends('btp_quote_status')
    def _compute_is_locked(self):
        for record in self:
            record.btp_is_locked = record.btp_quote_status in ('sent', 'accepted', 'refused', 'expired')

    @api.depends('btp_lot_ids', 'btp_lot_ids.title_ids', 'btp_lot_ids.title_ids.subtitle_ids',
                 'btp_lot_ids.title_ids.subtitle_ids.item_ids', 'btp_lot_ids.title_ids.subtitle_ids.item_ids.total_cost',
                 'amount_total')
    def _compute_btp_totals(self):
        for record in self:
            # Calculate total cost from all items
            total_cost = 0.0
            for lot in record.btp_lot_ids:
                for title in lot.title_ids:
                    for subtitle in title.subtitle_ids:
                        for item in subtitle.item_ids:
                            total_cost += item.total_cost

            record.btp_total_cost = total_cost
            record.btp_total_margin = record.amount_total - total_cost
            if record.amount_total > 0:
                record.btp_margin_percent = (record.btp_total_margin / record.amount_total) * 100
            else:
                record.btp_margin_percent = 0.0

    @api.depends('btp_sent_date', 'date_order')
    def _compute_days_to_send(self):
        for record in self:
            try:
                if record.btp_sent_date and record.date_order:
                    # Both are Datetime fields
                    sent_date = record.btp_sent_date
                    order_date = record.date_order
                    # Convert to date if datetime objects
                    if hasattr(sent_date, 'date'):
                        sent_date = sent_date.date()
                    if hasattr(order_date, 'date'):
                        order_date = order_date.date()
                    # Calculate difference
                    if sent_date and order_date:
                        delta = sent_date - order_date
                        record.btp_days_to_send = delta.days
                    else:
                        record.btp_days_to_send = 0
                else:
                    record.btp_days_to_send = 0
            except Exception as e:
                _logger.warning("Error computing days_to_send for quote %s: %s", record.id, str(e))
                record.btp_days_to_send = 0

    @api.depends('state')
    def _compute_is_converted(self):
        for record in self:
            record.btp_is_converted = record.state in ('sale', 'done')

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate quote number"""
        orders = super(SaleOrder, self).create(vals_list)
        for order in orders:
            if not order.btp_quote_number:
                order.btp_quote_number = order._generate_quote_number(order.date_order)
        orders._btp_apply_company_commercial_conditions()
        return orders

    @api.onchange('partner_id', 'company_id')
    def _onchange_btp_apply_company_commercial_conditions(self):
        self._btp_apply_company_commercial_conditions()

    def action_confirm(self):
        self._btp_validate_subcontractor_documents()
        result = super().action_confirm()
        for order in self:
            order._btp_ensure_site()
            if order.btp_site_id and order.btp_site_id.btp_is_blocked:
                raise UserError(_(
                    'Site "%s" is blocked because mandatory documents are missing or expired. '
                    'Please resolve document checklist issues before confirming commercial operations.'
                ) % order.btp_site_id.display_name)
        return result

    def _btp_ensure_site(self):
        for order in self:
            if order.btp_site_id:
                continue
            vals = order._btp_prepare_site_vals()
            site = self.env['project.project'].create(vals)
            order.btp_site_id = site.id

    def _btp_prepare_site_vals(self):
        self.ensure_one()
        partner = self.partner_shipping_id or self.partner_id
        end_planned = self.commitment_date.date() if self.commitment_date else False
        if not end_planned and self.validity_date:
            end_planned = self.validity_date
        name_parts = [self.partner_id.name or _('Client')]
        if self.btp_quote_number:
            name_parts.append(self.btp_quote_number)
        else:
            name_parts.append(self.name)
        return {
            'name': ' - '.join(name_parts),
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id.id,
            'btp_site_address': partner.street or '',
            'btp_site_city': partner.city or '',
            'btp_site_zip': partner.zip or '',
            'btp_site_country_id': partner.country_id.id if partner.country_id else False,
            'btp_site_latitude': partner.partner_latitude or 0.0,
            'btp_site_longitude': partner.partner_longitude or 0.0,
            'btp_start_date': fields.Date.today(),
            'btp_end_date_planned': end_planned,
            'btp_sale_order_id': self.id,
        }

    def write(self, vals):
        """Override write to handle quote locking and revisions"""
        # Check if quote is locked
        if any(quote.btp_is_locked for quote in self):
            locked_fields = {
                'btp_lot_ids', 'order_line', 'partner_id', 'date_order',
                'pricelist_id', 'payment_term_id', 'partner_invoice_id',
                'partner_shipping_id'
            }
            if any(key in vals for key in locked_fields):
                raise UserError(_('Cannot modify a sent/accepted/refused quote. Create a revision instead.'))

        # Sync status with sale order state when state changes
        if 'state' in vals and 'btp_quote_status' not in vals:
            state_map = {
                'draft': 'draft',
                'sent': 'sent',
                'sale': 'accepted',
                'done': 'accepted',
                'cancel': 'refused',
            }
            mapped = state_map.get(vals.get('state'))
            if mapped:
                vals['btp_quote_status'] = mapped

        # Handle status change to 'sent'
        if vals.get('btp_quote_status') == 'sent':
            for quote in self:
                if not quote.btp_sent_date:
                    quote.btp_sent_date = fields.Datetime.now()

        result = super(SaleOrder, self).write(vals)
        if any(k in vals for k in ('partner_id', 'company_id')):
            self._btp_apply_company_commercial_conditions()
        return result

    def _btp_apply_company_commercial_conditions(self):
        """Apply client commercial conditions for the order company when available."""
        if self.env.context.get('btp_skip_apply_conditions'):
            return
        Condition = self.env['btp.company.commercial.condition']
        for order in self:
            if not order.partner_id or not order.company_id:
                continue
            cond = Condition.search([
                ('partner_id', '=', order.partner_id.id),
                ('company_id', '=', order.company_id.id),
            ], limit=1)
            if not cond:
                continue
            vals = {}
            if cond.pricelist_id:
                vals['pricelist_id'] = cond.pricelist_id.id
            if cond.payment_term_id:
                vals['payment_term_id'] = cond.payment_term_id.id
            # Keep compatibility with sale.order field naming across versions.
            if cond.incoterm_id:
                if 'incoterm_id' in order._fields:
                    vals['incoterm_id'] = cond.incoterm_id.id
                elif 'incoterm' in order._fields:
                    vals['incoterm'] = cond.incoterm_id.id
            if not vals:
                continue
            if order.id:
                order.with_context(btp_skip_apply_conditions=True).write(vals)
            else:
                order.update(vals)

    def _generate_quote_number(self, date_order=None):
        """Generate quote number in format YYYYMMNNN using an ir.sequence with monthly ranges."""
        seq_date = date_order or fields.Datetime.now()
        sequence = self.env['ir.sequence'].next_by_code('btp.quote', sequence_date=seq_date)
        if not sequence:
            raise UserError(_('Quote sequence is not configured.'))
        return sequence

    def action_create_revision(self):
        """Create a revision of this quote"""
        if not self.btp_is_locked:
            raise UserError(_('Can only create revisions of sent quotes.'))
        
        # Determine next revision letter
        existing_revisions = self.btp_revision_ids.mapped('btp_revision_index')
        if existing_revisions:
            last_revision = max(existing_revisions)
            next_letter = chr(ord(last_revision) + 1)
        else:
            next_letter = 'A'
        
        if ord(next_letter) > ord('Z'):
            raise UserError(_('Maximum number of revisions (26) reached.'))
        
        # Create copy
        revision = self.copy({
            'btp_quote_number': self.btp_quote_number,
            'btp_revision_index': next_letter,
            'btp_original_quote_id': self.id,
            'btp_quote_status': 'draft',
            'btp_sent_date': False,
            'state': 'draft',
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Quote Revision'),
            'res_model': 'sale.order',
            'res_id': revision.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_send_quote(self):
        """Send quote to client"""
        if self.btp_quote_status != 'draft':
            raise UserError(_('Only draft quotes can be sent.'))
        self._btp_validate_subcontractor_documents()
        
        # Validate quote structure
        if not self.btp_lot_ids:
            raise UserError(_('Quote must have at least one lot.'))
        
        # Check consistency
        for lot in self.btp_lot_ids:
            if not lot.title_ids:
                raise UserError(_('Lot "%s" must have at least one title.') % lot.name)
            for title in lot.title_ids:
                if not title.subtitle_ids:
                    raise UserError(_('Title "%s" must have at least one subtitle.') % title.name)
                for subtitle in title.subtitle_ids:
                    if not subtitle.item_ids:
                        raise UserError(_('Subtitle "%s" must have at least one item.') % subtitle.name)
        
        # Trigger Odoo's standard sending flow (email + signature if enabled)
        action = self.action_quotation_send()

        # Update status and follow-up date
        followup_delay = int(self.env['ir.config_parameter'].sudo().get_param(
            'btp_prospecting.quote_followup_delay_days', 7
        ))
        next_followup = fields.Date.today() + timedelta(days=followup_delay)
        self.write({
            'btp_quote_status': 'sent',
            'btp_sent_date': fields.Datetime.now(),
            'btp_next_followup_date': self.btp_next_followup_date or next_followup,
        })

        return action

    def action_send_quote_reminder(self):
        """Open mail composer with Module 12 quote reminder template."""
        self.ensure_one()
        action = self.action_quotation_send()
        template = self.env.ref('btp_prospecting.email_template_btp_quote_reminder', raise_if_not_found=False)
        if not template:
            template = self.env['mail.template'].search([
                ('name', '=', 'BTP Quote: Reminder'),
                ('model_id.model', '=', 'sale.order'),
            ], limit=1)
        if not template:
            raise UserError(_(
                'Email template "BTP Quote: Reminder" was not found. '
                'Please upgrade module "btp_prospecting" or create the template in Settings > Technical > Email > Templates.'
            ))
        ctx = dict(action.get('context', {}) or {})
        ctx.update({
            'default_use_template': True,
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
        })
        action['context'] = ctx
        return action

    def _btp_validate_subcontractor_documents(self):
        """Block quote send/confirm when subcontractor compliance docs are invalid."""
        subcontractors = self.env['res.partner']
        for order in self:
            for lot in order.btp_lot_ids:
                for title in lot.title_ids:
                    for subtitle in title.subtitle_ids:
                        for item in subtitle.item_ids:
                            for labor in item.labor_ids.filtered(
                                lambda l: l.labor_type == 'subcontracting' and l.subcontractor_id
                            ):
                                subcontractors |= labor.subcontractor_id
        if subcontractors:
            subcontractors._btp_validate_subcontractor_documents_or_raise()

    def _cron_quote_followup(self):
        """Send follow-up reminders for quotes that need follow-up."""
        today = fields.Date.today()
        quotes = self.search([
            ('btp_next_followup_date', '<=', today),
            ('btp_next_followup_date', '!=', False),
            ('btp_quote_status', '=', 'sent'),
        ])
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        followup_delay = int(self.env['ir.config_parameter'].sudo().get_param(
            'btp_prospecting.quote_followup_delay_days', 7
        ))
        for quote in quotes:
            if not activity_type:
                continue
            existing = self.env['mail.activity'].search([
                ('res_model', '=', 'sale.order'),
                ('res_id', '=', quote.id),
                ('activity_type_id', '=', activity_type.id),
                ('summary', 'ilike', 'Quote follow-up'),
            ], limit=1)
            if existing:
                continue
            self.env['mail.activity'].create({
                'res_model': 'sale.order',
                'res_id': quote.id,
                'activity_type_id': activity_type.id,
                'summary': _('Quote follow-up: %s') % (quote.btp_quote_number or quote.name),
                'note': _('Follow up with the client for this quote.'),
                'date_deadline': quote.btp_next_followup_date,
                'user_id': quote.user_id.id or quote.create_uid.id,
            })
            quote.btp_next_followup_date = today + timedelta(days=followup_delay)

