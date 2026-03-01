# -*- coding: utf-8 -*-
# Part of BTP Prospecting. See LICENSE for details.
# Module 13 — Multi-companies: company-level sharing policy and identification.

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Legal / identification (optional; base has company_registry / vat)
    btp_siren = fields.Char(
        string='SIREN',
        size=9,
        help='9-digit SIREN number for this company (French legal identifier).',
    )

    # Sharing policy flags: when True, this company uses shared data with other entities.
    btp_shared_clients = fields.Boolean(
        string='Use Shared Clients',
        default=False,
        help='When enabled, this company can use clients shared with other companies (same legal file, distinct commercial conditions).',
    )
    btp_shared_suppliers = fields.Boolean(
        string='Use Shared Suppliers',
        default=False,
        help='When enabled, this company can use suppliers/subcontractors shared with other companies.',
    )
    btp_shared_articles = fields.Boolean(
        string='Use Shared Articles',
        default=False,
        help='When enabled, this company uses the common article catalog; prices and conditions remain per company.',
    )
