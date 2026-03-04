# -*- coding: utf-8 -*-
{
    'name': 'BTP Prospecting & Lead Management',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Comprehensive lead management and client/contact management system for Building and Public Works industry',
    'description': """
BTP Prospecting & Lead Management + Clients & Contacts Management
===================================================================
This module provides a complete lead management and client/contact management solution 
specifically designed for the Building and Public Works (BTP) industry.

Module 1 - Lead Management:
----------------------------
* Multi-channel lead capture (mobile, web, import, AI)
* Pyramidal attribution and visibility control
* Qualification workflow (Field → Targeting → Contact → Decision)
* Automated reminders and escalations (D0, +15, +30 days)
* Anti-duplicate detection and merging
* Multi-company lead sharing
* Site-centric lead management
* KPI dashboards and reporting
* Integration with messaging, calls, and tasks

Module 2 - Clients & Contacts Management:
-----------------------------------------
* Company hierarchy management (Group → Subsidiary → Agency)
* Unique client base with SIREN/SIRET validation
* Contact career history tracking across companies
* Anti-duplicate controls (companies and contacts)
* External API integration (INSEE/Pappers/Infogreffe) for company enrichment
* Pyramidal access rights and attribution logic
* Multi-company client sharing with distinct commercial conditions
* Reports and KPIs (active clients, coverage rate, career history)

Module 3 - Quotes & Articles:
-------------------------------
* Hierarchical quote structure (Lot → Title → Subtitle → Item)
* Centralized article base with families and subfamilies
* Article document management (TS, PV, SDS, notices) with expiration alerts
* Price history tracking by supplier
* Supplier and subcontractor management with hierarchy
* Regulatory document management (URSSAF, taxes, insurances) with expiration alerts
* Quote numbering system (YYYYMMNNN format with alphabetical revisions)
* Quote workflow (creation, control, sending, follow-up)
* Labor calculation (internal yield or subcontracting)
* Quote-to-order conversion tracking

Module 7 - Invoicing & Situations:
----------------------------------
* Monthly progress situations (item-by-item: cumul M, M-1, month progress, balance)
* Deposit and final invoicing; retention of guarantee (default 5%, configurable per site)
* Invoice numbering YYYYMMNNN + alphabetical revision index
* Payment/reminder follow-up (D-7, D0, D+15, D+30, formal notice)

Module 8 - Payments &amp; Finances:
-----------------------------------
* Client payments follow-up (outstanding, HT/TTC, due date, paid, balance, color codes)
* Supplier/subcontractor payments follow-up (outstanding, due date, status)
* Financial forecasts (cash plan: inflows/outflows by period, filter by site/company)
* Analytical margins by site (quote vs actual, net margin, forecast vs actual)
* Banking: use Odoo bank statements and reconciliation
* Multi-company consolidation views

Module 9 - Stocks &amp; Logistics:
----------------------------------
* Multi-warehouses (headquarters, agencies, site depots) with BTP site link on locations
* Stock moves linked to site and origin type (client order, site consumption, transfer, etc.)
* Reservation from client order (sale_stock); delivery moves carry BTP site
* Site consumptions optionally linked to stock moves; outbound from consumption
* Inventory and valuation (FIFO/standard via Odoo Stock)
* Reports: stock by warehouse/location, consumption by site, reserved vs available
* Module 10 - Quality &amp; Safety (QHSE): QHSE incidents and corrective actions per site; documents (PPSPS, DOE, certificates) via Site Documents
* Module 11 - Reports &amp; Exports: configurable report templates (by lot, site, client, salesperson, article, supplier, QHSE); PDF/Excel/CSV; scheduled sending by email; export history
* Module 13 - Multi-companies: company selection and switching; strict data separation; shared clients/suppliers/articles and commercial conditions per company; shared leads; consolidated reports (turnover, cash, margin, shared clients distribution)
* Module 14 - Mobile (optional): JSON API for PWA and native apps (leads, partners, quotes, sites, pointing, yield, QHSE incidents, tasks, dashboard, notifications); use Odoo PWA for mobile web access
* Module 15 - Synthesis &amp; System Governance: hierarchical access (N/N-1/N-2/Management), audit log (who, when, why), reattribution with reason, temporary rights; anti-duplicate (clients, suppliers SIREN, leads); automatic reattribution of inactive clients; governance reports (data quality, reattributions); consolidated management views
    """,
    'author': 'BTP Solutions',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'contacts',
        'crm',
        'sale',
        'sale_stock',
        'project',
        'purchase',
        'stock',
        'account',
        'web_tour',
        'spreadsheet_dashboard',
        'calendar',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'data': [
        'security/btp_prospecting_security.xml',
        'security/ir.model.access.csv',
        'security/btp_audit_log_access.xml',
        'data/btp_lead_stage_data.xml',
        'data/btp_lead_reminder_cron.xml',
        'data/btp_document_expiration_cron.xml',
        'data/btp_site_sequence.xml',
        'data/btp_quote_sequence.xml',
        'data/btp_quote_item_product.xml',
        'data/btp_quote_followup_cron.xml',
        'data/btp_site_document_cron.xml',
        'data/btp_yield_escalation_cron.xml',
        'data/btp_qse_incident_sequence.xml',
        'data/btp_invoice_sequence.xml',
        'data/btp_invoice_reminder_cron.xml',
        'data/btp_ai_seed.xml',
        'data/btp_ai_cron.xml',
        'data/btp_email_templates.xml',
        'views/btp_lead_wizard_views.xml',
        'views/btp_lead_views.xml',
        'views/btp_lead_stage_views.xml',
        'views/btp_lead_assignment_rule_views.xml',
        'views/res_users_views.xml',
        'views/btp_company_hierarchy_views.xml',
        'views/btp_supplier_views.xml',  # before res_partner_views so DB view 1393 is updated first
        'views/res_partner_views.xml',
        'views/btp_company_search_views.xml',
        'views/btp_company_site_views.xml',
        'views/btp_article_views.xml',
        'views/btp_site_views.xml',
        'views/btp_planning_views.xml',
        'views/btp_site_document_views.xml',
        'views/btp_qse_incident_views.xml',
        'views/btp_site_reports_views.xml',
        'views/btp_quote_views.xml',
        'views/btp_quote_reports_views.xml',
        'views/btp_supplier_search_views.xml',
        'views/res_config_settings_views.xml',
        'views/btp_situation_views.xml',
        'views/btp_deposit_invoice_wizard_views.xml',
        'views/btp_invoice_views.xml',
        'views/btp_outstanding_actions.xml',  # before outstanding views (they reference these actions)
        'views/btp_client_outstanding_views.xml',
        'views/btp_supplier_outstanding_views.xml',
        'views/btp_cash_forecast_views.xml',
        'views/btp_site_margin_views.xml',
        'views/btp_bank_statement_views.xml',
        'wizard/btp_bank_statement_import_wizard_views.xml',
        'views/btp_stock_views.xml',
        'views/btp_dashboard_views.xml',
        'views/btp_report_views.xml',
        'views/btp_call_report_views.xml',
        'views/btp_calendar_views.xml',
        'views/btp_multi_company_views.xml',
        'views/btp_governance_views.xml',
        'views/btp_prospecting_menus.xml',
        'views/btp_ai_views.xml',
        'reports/btp_lead_reports.xml',
        'reports/btp_lead_templates.xml',
        'reports/btp_report_generic_reports.xml',
        'reports/btp_report_generic_templates.xml',
        'data/btp_report_schedule_cron.xml',
        'data/btp_activity_escalation_cron.xml',
        'data/btp_reattribution_cron.xml',
    ],
    'demo': [
        'demo/btp_lead_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'btp_prospecting/static/src/scss/btp_prospecting.scss',
        ],
    },
    'pre_init_hook': 'btp_prospecting.hooks.pre_init_hook_res_company_btp',
    'post_init_hook': 'btp_prospecting.hooks.post_init_hook_qse_attachment_migration',
    'installable': True,
    'application': True,
    'auto_install': False,
}

