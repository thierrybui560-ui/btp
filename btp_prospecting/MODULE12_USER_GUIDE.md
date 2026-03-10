# Module 12 — Third Parties & Integrated Messaging

## 1) Objectives & Scope

Module 12 centralizes third-party communication and follow-up execution in Odoo:

- keep calls, meetings, and email exchanges attached to business records,
- convert exchange outcomes into assigned actions,
- enforce reminder cadence and escalation workflow,
- provide traceability for management.

This guide is both a user guide and a UAT checklist.

---

## 2) Requirement-to-Implementation Matrix

| Requirement | Status | Implementation |
| --- | --- | --- |
| Third-party exchange centralization | Implemented | `btp.call.report` + chatter usage on partner/lead/site/quote |
| Email sending from Odoo records | Implemented | Native chatter send + templates (`btp_email_templates.xml`) |
| Incoming/outgoing attachment to relevant files | Partially implemented | Odoo thread matching + partner/record chatter; depends on mail gateway/routing setup |
| Manual business linking (site/opportunity) | Implemented | `btp_site_id`, `btp_lead_id`, `sale_order_id` on call/meeting report |
| Call and appointment reports | Implemented | `btp.call.report` model + menu/views |
| Task creation from reports | Implemented (improved) | `action_create_tasks()` creates `mail.activity` from action lines |
| Assign to several collaborators | Implemented (improved) | `assigned_user_ids` on action line, one task per collaborator |
| Mandatory meeting report follow-up | Implemented (improved) | Auto reminder activity on past BTP-linked meetings with no report |
| Reminders D / D+15 / D+30 | Implemented (improved) | `mail.activity` cron: `_cron_btp_send_activity_reminders()` |
| Escalation to manager after 30 days | Implemented (fixed) | `_cron_btp_escalate_overdue_activities()` now escalates at D+30 |

---

## 3) Menus, Models, and Key Fields

### 3.1 Menus

- `BTP Prospecting -> Third Parties & Messaging -> Call / Meeting Reports`
- `Calendar` app (event form extended with BTP fields)
- `Settings -> Technical -> Automation -> Scheduled Actions` (reminders/escalation crons)

### 3.2 Main Models

- `btp.call.report`: call/meeting report header
- `btp.call.report.action`: follow-up action lines
- `calendar.event` (extended): meeting link to BTP lead/site + report actions
- `mail.activity` (extended): reminder and escalation tracking flags

### 3.3 Key Fields

- **Report header**: `name`, `report_type`, `partner_id`, `btp_site_id`, `btp_lead_id`, `sale_order_id`, `date`, `summary`, `decision`, `calendar_event_id`
- **Action lines**: `name`, `deadline_date`, `assigned_to_id`, `assigned_user_ids`, `mail_activity_id`, `mail_activity_ids`
- **Calendar links**: `btp_site_id`, `btp_lead_id`, `btp_call_report_ids`, `btp_call_report_count`
- **Activity lifecycle**: `btp_reminder_d_sent`, `btp_reminder_d15_sent`, `btp_reminder_d30_sent`, `btp_escalated`

---

## 4) Scheduled Automations

### 4.1 Reminder Milestones

- **Method**: `mail.activity._cron_btp_send_activity_reminders()`
- **Trigger**: executed by the daily activity scheduler flow (same run as escalation cron).
- **Behavior**:
  - D: on deadline date
  - D+15: 15+ days after deadline
  - D+30: 30+ days after deadline
  - writes reminder trace in chatter + sends email to assignee when email exists

### 4.2 Escalation Cron

- **Name**: `BTP: Escalate Overdue Activities to Manager`
- **Method**: `mail.activity._cron_btp_escalate_overdue_activities()`
- **Behavior**:
  - escalates only when deadline is 30+ days overdue,
  - creates a manager task/activity on same business record,
  - marks original activity `btp_escalated = True` to prevent duplicate escalation.

---

## 5) User Procedures

## 5.1 Create a Call/Meeting Report

1. Open `Call / Meeting Reports` and click `New`.
2. Fill:
   - Subject, Type (`Call` or `Meeting`),
   - Third Party (required),
   - optional links: Site, Lead/Opportunity, Quote/Order.
3. Complete summary and decision.
4. Add follow-up action lines with deadline and assignee(s).
5. Save.

Expected:
- report is visible in list and traceable from related records.

## 5.2 Create Tasks From Actions

1. Open report with action lines.
2. Ensure each line has `Deadline`.
3. Set either:
   - `Assigned To` (single), or
   - `Assigned Collaborators` (multiple users).
4. Click `Create Tasks from Actions`.

Expected:
- one `mail.activity` is created per assigned collaborator,
- line stores created task links,
- reminders/escalation can process these activities later.

## 5.3 Link Meeting to BTP Business Context

1. Open `Calendar`, create/edit meeting.
2. Set `BTP Site` and/or `BTP Lead`.
3. Save.
4. Use:
   - `Create Meeting Report` button, or
   - `Open Reports` button to view linked reports.

Expected:
- event and meeting report remain linked through `calendar_event_id`,
- report count updates on the event.

---

## 6) Acceptance Scenarios (S1-S5)

## S1 — Client email with attachment routed to files

Goal: validate incoming email archival.

Steps:
1. Configure incoming mail connector (fetchmail/alias) and SMTP.
2. Send test email from client with attachment to routed mailbox.
3. Check chatter on client partner and related business record (if thread matched).

Expected:
- email and attachment visible in Odoo chatter,
- linked to third party; business linkage depends on thread/alias configuration.

Failure checks:
- no incoming mail server polling,
- unmatched alias/thread, unknown sender address mapping.

## S2 — Quote reminder from opportunity/quote

Goal: validate outbound logging and client archive.

Steps:
1. Open quote/opportunity record.
2. Send email with template `BTP Quote: Reminder`.
3. Confirm sent message appears in chatter.

Expected:
- outgoing email logged on quote/opportunity,
- client conversation archive visible on partner side when partner linked.

## S3 — Incoming call -> report -> task in 48h

Goal: convert call to actionable task.

Steps:
1. Create report type `Call`.
2. Add action `Send quote within 48h`.
3. Set assignee and deadline.
4. Click `Create Tasks from Actions`.

Expected:
- activity created for assignee with right deadline and summary.

## S4 — Site appointment -> report -> tasks for 2 employees

Goal: validate multi-collaborator assignment.

Steps:
1. Create calendar meeting linked to BTP site.
2. Create meeting report from event.
3. Add one action line with two `Assigned Collaborators`.
4. Create tasks from actions.

Expected:
- one task per collaborator,
- both users see reminder activities.

## S5 — Reminder escalation at D+30

Goal: validate delayed escalation policy.

Steps:
1. Create task activity with deadline older than 30 days.
2. Ensure assignee has manager set.
3. Run cron `BTP: Escalate Overdue Activities to Manager`.

Expected:
- manager receives escalation activity,
- original activity flagged escalated,
- no escalation before D+30 threshold.

Pass/Fail:
- Pass only if escalation is generated at D+30 and not earlier.

---

## 7) Troubleshooting Matrix

| Problem | Root cause to check | Corrective action |
| --- | --- | --- |
| Tasks not created from report | Missing deadline on action line | Fill `Deadline` and retry |
| Only one assignee receives task | `Assigned Collaborators` empty | Add multiple users on action line |
| No reminder emails | User email empty / SMTP down | Fill user email, verify outgoing mail |
| No meeting report reminder | Event not in past or not BTP linked | Set `BTP Site` or `BTP Lead` and close past event |
| No escalation | Deadline not yet D+30 / no manager | Check age of deadline and user manager |
| Incoming email not attached to business | Mail alias/thread mismatch | Verify incoming routing and document alias configuration |

---

## 8) Evidence Checklist for UAT Sign-off

- Screenshot/report list showing call/meeting report creation.
- Screenshot of action lines with multi-collaborator assignment.
- Screenshot of partner activities created from report.
- Screenshot of calendar event with linked report count.
- Reminder cron run evidence (mail/activity trace in chatter).
- Escalation evidence on manager activity inbox at D+30.

---

## 9) Final Sign-off Table

| Scenario | Tester | Date | Result | Notes |
| --- | --- | --- | --- | --- |
| S1 incoming email routing |  |  | Pass/Fail |  |
| S2 quote reminder archive |  |  | Pass/Fail |  |
| S3 call -> task |  |  | Pass/Fail |  |
| S4 meeting -> multi-user tasks |  |  | Pass/Fail |  |
| S5 D+30 escalation |  |  | Pass/Fail |  |

