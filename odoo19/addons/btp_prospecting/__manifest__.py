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
        'project',
        'purchase',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'data': [
        'security/btp_prospecting_security.xml',
        'security/ir.model.access.csv',
        'data/btp_lead_stage_data.xml',
        'data/btp_lead_reminder_cron.xml',
        'data/btp_document_expiration_cron.xml',
        'data/btp_quote_sequence.xml',
        'data/btp_quote_item_product.xml',
        'data/btp_quote_followup_cron.xml',
        'data/btp_email_templates.xml',
        'views/btp_lead_wizard_views.xml',
        'views/btp_lead_views.xml',
        'views/btp_lead_stage_views.xml',
        'views/btp_lead_assignment_rule_views.xml',
        'views/res_users_views.xml',
        'views/btp_company_hierarchy_views.xml',
        'views/res_partner_views.xml',
        'views/btp_company_search_views.xml',
        'views/btp_company_site_views.xml',
        'views/btp_article_views.xml',
        'views/btp_supplier_views.xml',
        'views/btp_quote_views.xml',
        'views/btp_quote_reports_views.xml',
        'views/btp_supplier_search_views.xml',
        'views/btp_prospecting_menus.xml',
        'reports/btp_lead_reports.xml',
        'reports/btp_lead_templates.xml',
    ],
    'demo': [
        'demo/btp_lead_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'btp_prospecting/static/src/scss/btp_prospecting.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}

