# -*- coding: utf-8 -*-
{
    'name': 'BTP Prospecting & Lead Management',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Comprehensive lead management system for Building and Public Works industry',
    'description': """
BTP Prospecting & Lead Management
==================================
This module provides a complete lead management solution specifically designed
for the Building and Public Works (BTP) industry.

Key Features:
-------------
* Multi-channel lead capture (mobile, web, import, AI)
* Pyramidal attribution and visibility control
* Qualification workflow (Field → Targeting → Contact → Decision)
* Automated reminders and escalations (D0, +15, +30 days)
* Anti-duplicate detection and merging
* Multi-company lead sharing
* Site-centric lead management
* KPI dashboards and reporting
* Integration with messaging, calls, and tasks
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
    ],
    'data': [
        'security/btp_prospecting_security.xml',
        'security/ir.model.access.csv',
        'data/btp_lead_stage_data.xml',
        'data/btp_lead_reminder_cron.xml',
        'data/btp_email_templates.xml',
        'views/btp_lead_wizard_views.xml',
        'views/btp_lead_views.xml',
        'views/btp_lead_stage_views.xml',
        'views/btp_lead_assignment_rule_views.xml',
        'views/res_users_views.xml',
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

