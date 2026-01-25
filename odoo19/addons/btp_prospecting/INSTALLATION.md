# Installation & Setup Guide

## Prerequisites

- Odoo 19.0 installed and running
- Required modules: base, mail, contacts, crm, sale, project
- Database with at least one company configured
- User with administrator rights

## Installation Steps

### 1. Copy Module to Addons Directory

```bash
# Copy the btp_prospecting folder to your Odoo addons directory
# Example path: /usr/lib/python3/dist-packages/odoo/addons/btp_prospecting
# Or: /opt/odoo/addons/btp_prospecting
```

### 2. Update App List

1. Log in to Odoo as administrator
2. Go to **Apps** menu
3. Click **Update Apps List**
4. Remove the **Apps** filter to see all modules

### 3. Install the Module

1. Search for "BTP Prospecting" in the Apps menu
2. Click **Install**
3. Wait for the installation to complete

### 4. Configure User Groups

After installation, configure user groups:

1. Go to **Settings > Users & Companies > Groups**
2. Assign users to appropriate groups:
   - **BTP Salesperson**: For sales team members
   - **BTP Manager**: For sales managers
   - **BTP Administrator**: For system administrators

### 5. Set Up User Hierarchy (Pyramidal)

1. Go to **Settings > Users & Companies > Users**
2. For each user, set their **Manager** field
3. This enables pyramidal visibility (managers see subordinates' leads)

### 6. Configure Lead Stages

1. Go to **BTP Prospecting > Configuration > Lead Stages**
2. Review default stages:
   - New
   - Qualified
   - Contacted
   - To Remind
   - Decision
   - Won
   - Lost
3. Customize stages to match your workflow
4. Set qualification status for each stage
5. Configure reminder requirements

### 7. Set Up Assignment Rules (Optional)

1. Go to **BTP Prospecting > Configuration > Assignment Rules**
2. Create rules based on:
   - **Geography**: Assign by country, city, or ZIP code pattern
   - **Client Type**: Assign by partner categories
   - **Site Type**: Assign by site type (residential, commercial, etc.)
   - **Round Robin**: Distribute leads evenly among team members

Example Geography Rule:
- Name: "Paris Area Leads"
- Assignment Type: Geography
- ZIP Code Pattern: "75*"
- Assign To: [Select salesperson]

### 8. Verify Automated Jobs

The following cron jobs are automatically created:

1. **BTP Lead: Send Reminders** (runs hourly)
   - Sends reminders for leads due for follow-up

2. **BTP Lead: Escalate Stalled Leads** (runs daily)
   - Escalates leads stalled for 30+ days

3. **BTP Lead: 6-Month Loop Reminders** (runs daily)
   - Sends follow-up reminders for lost/unsuccessful leads

Verify they are active:
- Go to **Settings > Technical > Automation > Scheduled Actions**
- Search for "BTP Lead"
- Ensure all three jobs are active

### 9. Configure Email Templates (Optional)

Email templates are pre-configured but can be customized:

1. Go to **Settings > Technical > Email > Templates**
2. Search for "BTP Lead"
3. Customize templates as needed:
   - BTP Lead: Reminder
   - BTP Lead: Escalation
   - BTP Lead: 6-Month Loop Reminder

## Post-Installation Checklist

- [ ] Module installed successfully
- [ ] User groups assigned
- [ ] User hierarchy configured (manager relationships)
- [ ] Lead stages reviewed/customized
- [ ] Assignment rules created (if needed)
- [ ] Cron jobs active and running
- [ ] Email templates reviewed
- [ ] Test lead creation
- [ ] Test lead assignment
- [ ] Test reminder system

## Testing the Installation

### Test 1: Create a Lead

1. Go to **BTP Prospecting > Leads**
2. Click **Create**
3. Fill in:
   - Title: "Test Lead"
   - Origin: "Manual Entry"
   - Site Name: "Test Site"
4. Click **Save**
5. Verify lead is created

### Test 2: Claim an Open Lead

1. Create a lead and leave it as "Common Open"
2. Log in as a different salesperson
3. Open the lead
4. Click **Take Lead**
5. Verify lead is assigned to you

### Test 3: Test Assignment Rules

1. Create an assignment rule (e.g., geography-based)
2. Create a lead matching the rule criteria
3. Verify lead is auto-assigned according to the rule

### Test 4: Test Reminder System

1. Create a lead
2. Set next reminder date to today
3. Wait for cron job to run (or run manually)
4. Verify reminder activity/email is created

## Troubleshooting

### Issue: Module not appearing in Apps

**Solution:**
- Verify module is in correct addons directory
- Check file permissions
- Update Apps List
- Check Odoo logs for errors

### Issue: Permission errors

**Solution:**
- Verify user has correct group assigned
- Check record rules in Security settings
- Verify company access rights

### Issue: Cron jobs not running

**Solution:**
- Check if cron jobs are active
- Verify Odoo worker is running
- Check Odoo logs for cron errors
- Manually trigger cron jobs for testing

### Issue: Email templates not working

**Solution:**
- Verify email server is configured in Odoo
- Check email template syntax
- Verify user has email address
- Test email sending in Settings > Technical

### Issue: Assignment rules not working

**Solution:**
- Verify rule is active
- Check rule sequence (priority)
- Verify rule criteria match lead data
- Check company assignment in rule

## Next Steps

After installation and configuration:

1. Train users on lead management workflow
2. Set up reporting dashboards
3. Configure integrations (if needed)
4. Customize views and fields as needed
5. Set up data import templates
6. Create custom reports (if needed)

## Support

For issues or questions:
- Check Odoo logs: `/var/log/odoo/odoo.log`
- Review module documentation
- Contact system administrator

