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
        return orders

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

        return super(SaleOrder, self).write(vals)

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
        
        # Copy lots structure
        for lot in self.btp_lot_ids:
            new_lot = lot.copy({'quote_id': revision.id})
            for title in lot.title_ids:
                new_title = title.copy({'lot_id': new_lot.id})
                for subtitle in title.subtitle_ids:
                    new_subtitle = subtitle.copy({'title_id': new_title.id})
                    for item in subtitle.item_ids:
                        new_item = item.copy({'subtitle_id': new_subtitle.id})
                        # Copy articles and labor
                        for article in item.article_ids:
                            article.copy({'item_id': new_item.id})
                        for labor in item.labor_ids:
                            labor.copy({'item_id': new_item.id})
        
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

