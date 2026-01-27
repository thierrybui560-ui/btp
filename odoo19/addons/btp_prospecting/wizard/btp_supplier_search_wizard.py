# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class BtpSupplierSearchWizard(models.TransientModel):
    _name = 'btp.supplier.search.wizard'
    _description = 'Supplier/Subcontractor Search Wizard'

    search_type = fields.Selection([
        ('supplier', 'Supplier'),
        ('subcontractor', 'Subcontractor'),
    ], string='Type', required=True, default='supplier')
    siren = fields.Char(string='SIREN', size=9)
    name = fields.Char(string='Name')

    def _build_partner_vals(self, enriched_data):
        vals = {
            'is_company': True,
            'company_type': 'company',
            'is_supplier': self.search_type == 'supplier',
            'is_subcontractor': self.search_type == 'subcontractor',
            'btp_api_enriched': True,
        }
        vals.update(enriched_data or {})
        return vals

    def action_search_and_create(self):
        self.ensure_one()

        if not self.siren and not self.name:
            raise UserError(_('Please enter a SIREN or a name.'))

        # Try local search by name first if provided
        if self.name:
            existing = self.env['res.partner'].sudo().search([
                ('name', 'ilike', self.name),
                ('is_company', '=', True),
                ('is_supplier', '=', self.search_type == 'supplier'),
                ('is_subcontractor', '=', self.search_type == 'subcontractor'),
            ], limit=1)
            if existing:
                return self._open_partner(existing)

        # If SIREN is provided, enrich and create
        if self.siren:
            enriched_data = self.env['res.partner']._enrich_from_api(self.siren) or {}
            if not enriched_data:
                # Fallback to manual creation with prefilled SIREN
                return self._open_manual_with_defaults()

            vals = self._build_partner_vals(enriched_data)
            partner = self.env['res.partner'].sudo().create(vals)
            return self._open_partner(partner)

        raise UserError(_('No matching supplier or subcontractor found.'))

    def action_create_manual(self):
        self.ensure_one()
        return self._open_manual_with_defaults()

    def _open_manual_with_defaults(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Supplier/Subcontractor'),
            'res_model': 'res.partner',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_is_company': True,
                'default_company_type': 'company',
                'default_is_supplier': self.search_type == 'supplier',
                'default_is_subcontractor': self.search_type == 'subcontractor',
                'default_siren': self.siren,
                'default_name': self.name,
            },
        }

    def _open_partner(self, partner):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Supplier/Subcontractor'),
            'res_model': 'res.partner',
            'res_id': partner.id,
            'view_mode': 'form',
            'target': 'current',
        }

