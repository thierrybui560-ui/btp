# Module 12 — Third Parties & Integrated Messaging — User & Testing Guide

This guide helps you **use and test Module 12**: centralising exchanges with third parties (clients, suppliers, subcontractors), call/meeting reports, follow-up tasks, and reminder escalation. It is based on the current BTP Prospecting implementation (Odoo 19).

---

## 1. What Module 12 Does (Summary)

| Goal | What the system does |
|------|----------------------|
| **Centralise exchanges** | Emails, calls, and appointments are attached to the right files: third party (contact/company), site, opportunity (lead), and internal user. |
| **Email sending** | Send emails directly from Odoo (from client file, site, or opportunity) with optional templates (prospecting, quote reminder, invoice reminder) and attachments. |
| **Email reception** | Emails received in Odoo (e.g. via IMAP/SMTP) are attached automatically to the third party and, when possible, to the business file (site, quote, opportunity). |
| **Call / meeting reports** | For each call or meeting, record a report: summary, duration, interlocutor, decisions, and follow-up actions. Link to third party, site, opportunity. |
| **Tasks from reports** | Follow-up actions on a report can be turned into activities (tasks) on the third party with due dates; they feed the reminder table. |
| **Reminder escalation** | Overdue activities are escalated to the assignee’s manager (N+1) so they can reassign or take action. |
| **Calendar** | Appointments can be linked to a BTP site or lead/opportunity; agenda can sync with Outlook/Google (Odoo standard). |

---

## 2. Feature List (What You Can Test)

| # | Feature | Where to test | Section |
|---|---------|----------------|--------|
| F1 | **Call / meeting report** — Create report (call or meeting), third party, site, lead, summary, actions | Third Parties & Messaging → Call / Meeting Reports → New | 5.1 |
| F2 | **Create tasks from actions** — Turn report action lines into activities on the third party with deadlines | Report form → Create Tasks from Actions | 5.2 |
| F3 | **Email from file** — Send email from client, site, or opportunity; use template (quote reminder, prospecting) | Chatter on partner / site / lead; Send message or template | 5.3 |
| F4 | **Calendar + BTP** — Link meeting to BTP Site or BTP Lead | Calendar → Event form → BTP Site / BTP Lead | 5.4 |
| F5 | **Escalation** — Overdue activity → new activity for manager (N+1) | Leave activity overdue; cron runs daily | 5.5 |

---

## 3. Where to Find Everything (UI Navigation)

### 3.1 BTP menu: Third Parties & Messaging

| Menu path | What you see | Access |
|-----------|--------------|--------|
| **BTP Prospecting → Third Parties & Messaging → Call / Meeting Reports** | List and form of call/meeting reports. | BTP Salesperson+ (create/edit); Manager/Admin delete. |

### 3.2 Email and chatter

| Where | What |
|-------|------|
| **Contact/Company form** | Chatter: send message, attach files; emails sent/received are attached to the partner. |
| **Site (project) form** | Chatter: discuss site; link emails when the thread is linked to the site. |
| **Lead/Opportunity form** | Chatter: send message; use **Send Message** or **Email Template** (e.g. BTP Lead: Prospecting). |
| **Quote (sale order) form** | Chatter: send message; use template **BTP Quote: Reminder** for quote follow-up. |

### 3.3 Calendar

| Where | What |
|-------|------|
| **Calendar app** | Create/edit event; set **BTP Site** and/or **BTP Lead** to link the meeting to a site or opportunity. |

### 3.4 Access rights

- **Call / meeting report**: Salesperson read/create/write; Manager/Admin can delete.
- **Tasks (activities)** created from reports are on the third party (res.partner); same rights as for the partner.
- **Escalation**: Automatic; manager receives an activity when a subordinate’s activity is overdue (cron **BTP: Escalate Overdue Activities to Manager**).

---

## 4. Email Templates (Module 12)

| Template | Model | Use |
|----------|--------|-----|
| **BTP Quote: Reminder** | Sale Order | Send from a quote to remind the client (e.g. from opportunity file). |
| **BTP Lead: Prospecting** | BTP Lead | Send from a lead to prospect or follow up with the client. |
| **BTP Invoice: …** (D-7, D0, D+15, D+30, formal) | Invoice | Already used by Module 7 reminder workflow. |

Templates are in **Settings → Technical → Email → Templates** (or via **Send Message** → **Email Template** on a record).

---

## 5. Step-by-Step Tests

### 5.1 Create a call or meeting report (F1)

**Steps**

1. **BTP Prospecting → Third Parties & Messaging → Call / Meeting Reports** → **New**.
2. **Subject** = e.g. "Client X – call about quote".
3. **Type** = Call or Meeting.
4. **Third Party** = client, supplier, or subcontractor (required).
5. Optionally set **Site**, **Lead / Opportunity**, **Quote / Order**.
6. **Reported By** = current user (default).
7. **Date** = date/time of the call/meeting.
8. **Duration (min)** = e.g. 15.
9. **Interlocutor** = person spoken to (for calls).
10. In **Summary & Decision**: enter **Summary** and **Decision / Outcome**.
11. In **Follow-up Actions**: add lines (Action, Assigned To, Deadline, Details). Each action can later become a task.
12. Save.

**Expected**

- Report is saved; it appears in the list and on the third party’s chatter if linked. You can use **Create Tasks from Actions** once actions have deadlines.

### 5.2 Create tasks from actions (F2)

**Steps**

1. Open a **Call / Meeting Report** that has at least one **Follow-up Action** line.
2. For each action line, set **Assigned To** and **Deadline**.
3. Click **Create Tasks from Actions**.
4. You are redirected to the **Third Party** form.

**Expected**

- For each action line that does not yet have a task, a **mail activity** (To-Do) is created on the **third party** (res.partner) with the same summary, assignee, and deadline. The action line’s **Task** field is set. Activities appear in the partner’s **Activities** and in the **Reminders** (e.g. My Activities). If an action has no deadline, an error asks you to set one.

### 5.3 Send email from client / opportunity / quote (F3)

**Steps**

1. Open a **Contact** or **Company** (partner), or a **Lead**, or a **Quote** (sale order).
2. In the **Chatter**, click **Send message** or use the dropdown to choose **Email Template**.
3. For a quote: select **BTP Quote: Reminder**; complete and send.
4. For a lead: select **BTP Lead: Prospecting**; complete and send.
5. Add attachments (quote PDF, contract, etc.) if needed.

**Expected**

- The email is sent and a message is logged in the chatter; the email is attached to the third party and to the record (site/lead/quote) when applicable. Reception in Odoo depends on your mail server (IMAP/incoming) and gateway configuration.

### 5.4 Link calendar event to BTP site or lead (F4)

**Steps**

1. Open **Calendar** (or create an event from a partner/lead/site).
2. Create or edit an event.
3. Set **BTP Site** and/or **BTP Lead** (fields added by Module 12).
4. Save.

**Expected**

- The event is linked to the chosen site or lead (via Odoo’s resource link). It appears in the calendar and can be used for planning and follow-up. After the meeting, create a **Call / Meeting Report** and optionally link it to the same site/lead.

### 5.5 Reminder escalation (F5)

**Steps**

1. Create an **activity** (e.g. from a Call Report → Create Tasks from Actions) with a **deadline** in the past, assigned to a user who has a **Manager** set (Settings → Users → Manager).
2. Wait for the cron **BTP: Escalate Overdue Activities to Manager** to run (default: once per day), or run it manually from **Settings → Technical → Automation → Scheduled Actions**.
3. Check the **manager**’s activities / Reminders.

**Expected**

- A new **To-Do** activity is created for the manager, summarizing that the original task was overdue and who it was assigned to. The original activity is marked as escalated (`Escalated to Manager` = true) so it is not escalated again. The manager can reassign or complete the task.

---

## 6. Acceptance Scenarios (Spec Module 12)

### S1 — Client email: automatic attachment to site and salesperson

1. Client sends an email (with attachment) to a known address that is processed by Odoo (e.g. via incoming mail gateway).
2. **Verify**: The email is attached to the **third party** (client), and when the thread is linked to **Site Y** and **Salesperson Z**, it appears in the chatter of the site and is associated with the internal recipient.

*Note: Automatic routing to a specific site/salesperson depends on your mail gateway and Odoo’s mail thread matching (partner, document). Configure incoming mail and aliases accordingly.*

### S2 — Quote reminder: copy in client file

1. From an **Opportunity** or **Quote**, send an email using the **BTP Quote: Reminder** template (or type a reminder and send).
2. **Verify**: The sent message is logged in the chatter of the quote and of the **client** (partner), so the copy is archived in the client file.

### S3 — Incoming call → report → task

1. Secretary (or salesperson) creates a **Call Report**: Type = Call, Third Party = client, Summary = "Client asked for quote", Interlocutor = "Mr X".
2. Add a follow-up action: "Send quote within 48h", Assigned To = salesperson, Deadline = in 2 days.
3. Click **Create Tasks from Actions**.
4. **Verify**: A **To-Do** activity "Send quote within 48h" appears on the **client** (partner), assigned to the salesperson with the chosen deadline. It appears in the salesperson’s Reminders.

### S4 — Site appointment → report → tasks for 2 employees

1. Create a **Calendar** event linked to **BTP Site** (and optionally **BTP Lead**); add client/subcontractor as attendee.
2. After the meeting, create a **Call / Meeting Report**: Type = Meeting, Third Party = client or subcontractor, Site = same site, Summary and Decision filled.
3. Add two follow-up actions with different **Assigned To** and **Deadline** (e.g. project manager and salesperson).
4. Click **Create Tasks from Actions**.
5. **Verify**: Two activities are created on the third party, one per assignee, with their respective deadlines. Both appear in Reminders for the assigned users.

### S5 — Reminder escalation: task not done after 30 days → alert to manager

1. Create an activity on a partner with deadline in the past, assigned to a user who has **Manager** set.
2. Run the cron **BTP: Escalate Overdue Activities to Manager** (or wait for the scheduled run).
3. **Verify**: The manager receives a new activity (e.g. "Escalation: Overdue – [original summary] (was [assignee name])") with deadline today and a note indicating the original deadline and assignee. The original activity is marked as escalated. The manager can reassign or handle the task.

---

## 7. Troubleshooting

| Problem | What to check |
|--------|----------------|
| **Create Tasks from Actions fails** | Every action line must have a **Deadline**. Fill missing deadlines and try again. |
| **Tasks created on wrong record** | Tasks are created on the **third party** (partner) of the report. To have tasks on site or lead, use activities created manually on the site/lead or extend the action if you need different behaviour. |
| **No escalation** | Ensure the assignee has **Manager** set (Settings → Users → Manager). Ensure the cron **BTP: Escalate Overdue Activities to Manager** is active and runs (e.g. daily). Check that the activity’s deadline is in the past and that it was not already escalated. |
| **BTP Site / BTP Lead not on calendar** | Module 12 adds these fields to the calendar event form; the **Calendar** app must be installed and the view inheritance loaded. Upgrade the module if you do not see them. |
| **Email not attached to partner/site** | Incoming mail must be routed via Odoo (e.g. fetchmail, incoming gateway). Partner is matched by email address; linking to site/opportunity may require correct thread or document link. Check Mail settings and logs. |
| **Templates not in list** | Go to **Settings → Technical → Email → Templates**. Filter by model (e.g. Sale Order, BTP Lead) to find **BTP Quote: Reminder** and **BTP Lead: Prospecting**. |

---

## 8. Quick Reference — Key Fields

### Call / Meeting Report (btp.call.report)

| Field | Meaning |
|-------|--------|
| name | Subject of the call/meeting. |
| report_type | call / meeting. |
| partner_id | Third party (client, supplier, subcontractor) — required. |
| btp_site_id | BTP site (project). |
| btp_lead_id | Lead / opportunity. |
| sale_order_id | Quote or order. |
| user_id | Reported by (user). |
| date | Date/time of the call/meeting. |
| duration_minutes | Duration in minutes. |
| interlocutor | Person spoken to (calls). |
| summary | Summary of the exchange. |
| decision | Decision or outcome. |
| action_ids | Follow-up action lines (one-to-many). |
| calendar_event_id | Linked meeting event (if any). |

### Call Report Action (btp.call.report.action)

| Field | Meaning |
|-------|--------|
| call_report_id | Parent report. |
| name | Action description. |
| note | Details. |
| assigned_to_id | User to assign the task to. |
| deadline_date | Due date for the task. |
| mail_activity_id | Created activity (after Create Tasks from Actions). |

### Calendar Event (calendar.event, extended)

| Field | Meaning |
|-------|--------|
| btp_site_id | BTP site (project) linked to the event. |
| btp_lead_id | BTP lead/opportunity linked to the event. |

### Mail Activity (mail.activity, extended)

| Field | Meaning |
|-------|--------|
| btp_escalated | True when this overdue activity has been escalated to the manager. |

---

## 9. Summary Checklist

- **Call / Meeting Reports** are under **Third Parties & Messaging → Call / Meeting Reports**. Create reports for calls and meetings; link third party, site, lead, quote; add summary, decision, and follow-up actions.
- **Create Tasks from Actions** creates **mail activities** on the **third party** with due dates; set **Deadline** on each action before using it.
- **Email**: Use chatter on partner, site, lead, or quote to send messages; use **BTP Quote: Reminder** and **BTP Lead: Prospecting** templates where applicable. Incoming mail is attached to the partner and, when configured, to the business file.
- **Calendar**: Use **BTP Site** and **BTP Lead** on events to link meetings to sites and opportunities. Use Call / Meeting Reports after meetings to record outcomes and generate tasks.
- **Escalation**: Overdue activities are escalated to the assignee’s **Manager** by the cron **BTP: Escalate Overdue Activities to Manager**; ensure users have Manager set and the cron is active.
