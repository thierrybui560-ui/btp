# -*- coding: utf-8 -*-

from odoo import models, fields, _


class BtpCompanySearchWizard(models.TransientModel):
    _name = 'btp.company.search.wizard'
    _description = 'BTP Company Search Wizard'

    query = fields.Char(string='Company Name')
    siren = fields.Char(string='SIREN/SIRET')
    results = fields.Text(string='Results', readonly=True)

    def action_search(self):
        """Search companies by name or SIREN/SIRET without browsing the full base."""
        self.ensure_one()
        Partner = self.env['res.partner'].sudo()

        domain = [('is_company', '=', True)]
        conditions = []

        if self.query:
            conditions.append([('name', 'ilike', self.query)])
        if self.siren:
            conditions.append([('siren', '=', self.siren)])
            conditions.append([('siret', '=', self.siren)])

        if not conditions:
            self.results = _('Please provide a company name or SIREN/SIRET.')
            return {'type': 'ir.actions.act_window_close'}

        or_domain = ['|'] * (len(conditions) - 1) + [item for sublist in conditions for item in sublist]
        records = Partner.search(domain + or_domain, limit=10)

        if not records:
            self.results = _('No matching company found.')
            return {'type': 'ir.actions.act_window_close'}

        lines = []
        for rec in records:
            assigned = rec.btp_assigned_salesperson_id.name or _('Unassigned')
            siren = rec.siren or 'N/A'
            siret = rec.siret or 'N/A'
            lines.append(f"- {rec.name} | SIREN: {siren} | SIRET: {siret} | Assigned: {assigned}")

        self.results = '\n'.join(lines)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'btp.company.search.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

