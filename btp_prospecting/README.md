# BTP Prospecting & Lead Management

## Overview

This Odoo 19 module provides a comprehensive lead management solution specifically designed for the Building and Public Works (BTP) industry. It enables companies to capture, qualify, track, and convert leads from various sources with a focus on site-centric project management.

## Features

### Core Functionality

- **Multi-Channel Lead Capture**
  - Mobile app integration
  - Web forms
  - Social media integration
  - AI auto-search
  - File imports
  - Manual entry

- **Pyramidal Attribution & Visibility**
  - Hierarchical lead visibility (managers see subordinates' leads)
  - Common open leads (visible to all until claimed)
  - Automatic assignment rules (geography, client type, site type, round-robin)

- **Qualification Workflow**
  - Field → Targeting → Contact → Decision pipeline
  - Customizable stages
  - Mandatory reminders at each stage

- **Automated Follow-up System**
  - D0 reminders (immediate)
  - +15 day reminders
  - +30 day reminders
  - Automatic escalation to management after 30 days
  - 6-month loop reminders for lost/unsuccessful leads

- **Anti-Duplicate Detection**
  - Automatic duplicate detection on creation
  - Merge wizard with history preservation
  - Duplicate flagging and linking

- **Multi-Company Support**
  - Exclusive, shared, and global lead sharing
  - Per-company tracking and visibility

- **Site-Centric Management**
  - Site name, address, type
  - Project dates and duration
  - Tender deadlines
  - Site-specific information

- **Integration**
  - Messaging (emails auto-attached)
  - Calls and meetings tracking
  - Conversion to CRM opportunities
  - Conversion to sale quotes

- **Reporting & KPIs**
  - Lead conversion rates
  - Aging analysis
  - Performance dashboards
  - Custom reports

## Installation

1. Copy the `btp_prospecting` folder to your Odoo addons directory
2. Update the app list in Odoo
3. Install the module from Apps menu

## Dependencies

- base
- mail
- contacts
- crm
- sale
- project

**Optional:**
- website (for web form lead capture - templates need to be created separately)

## Configuration

### User Groups

- **BTP Salesperson**: Can create and manage own leads, claim open leads
- **BTP Manager**: Can see subordinates' leads, manage stages and rules
- **BTP Administrator**: Full access to all features

### Setting Up Assignment Rules

1. Go to BTP Prospecting > Configuration > Assignment Rules
2. Create rules based on:
   - Geography (country, city, ZIP code pattern)
   - Client type (partner categories)
   - Site type
   - Round-robin distribution

### Setting Up Stages

1. Go to BTP Prospecting > Configuration > Lead Stages
2. Customize stages to match your workflow
3. Set qualification status for each stage
4. Configure reminder requirements

## Usage

### Creating a Lead

1. Go to BTP Prospecting > Leads
2. Click Create
3. Fill in minimum required fields:
   - Title
   - Origin
   - Site information (optional but recommended)
4. Lead will be auto-assigned based on rules or left as open

### Claiming an Open Lead

1. View open leads from the menu
2. Click "Take Lead" button on the lead form
3. Lead is now assigned to you

### Converting a Lead

1. Open the lead
2. Complete qualification
3. Click "Convert to Opportunity"
4. Lead is converted to CRM opportunity

### Managing Duplicates

1. System automatically detects potential duplicates
2. Review duplicates in the "Duplicates" tab
3. Use the merge wizard to combine duplicates

## Technical Details

### Models

- `btp.lead`: Main lead model
- `btp.lead.stage`: Pipeline stages
- `btp.lead.assignment.rule`: Auto-assignment rules
- `btp.lead.tag`: Lead tags for categorization

### Automated Jobs

- **Reminder Cron**: Runs hourly, sends reminders for leads due
- **Escalation Cron**: Runs daily, escalates stalled leads (30+ days)
- **Loop Reminder Cron**: Runs daily, sends 6-month follow-ups

### Security

- Pyramidal record rules based on user hierarchy
- Multi-company record rules
- Group-based access control

## Development

### Code Structure

```
btp_prospecting/
├── models/
│   ├── btp_lead.py          # Main lead model
│   ├── btp_lead_stage.py    # Stages and assignment rules
│   └── res_users.py         # User hierarchy extension
├── views/
│   ├── btp_lead_views.xml
│   ├── btp_lead_stage_views.xml
│   └── btp_lead_assignment_rule_views.xml
├── controllers/
│   └── btp_lead_controller.py  # Web and mobile endpoints
├── wizard/
│   ├── btp_lead_merge_wizard.py
│   └── btp_lead_assign_wizard.py
├── security/
│   ├── btp_prospecting_security.xml
│   └── ir.model.access.csv
├── data/
│   ├── btp_lead_stage_data.xml
│   ├── btp_lead_reminder_cron.xml
│   └── btp_email_templates.xml
└── reports/
    ├── btp_lead_reports.xml
    └── btp_lead_templates.xml
```

## License

LGPL-3

## Author

BTP Solutions

## Support

For issues, questions, or contributions, please contact the development team.

