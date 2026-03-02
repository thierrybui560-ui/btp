# Module 15 — Synthesis & System Governance — User & Testing Guide

This guide describes **Module 15** features: hierarchical access, data security and audit, anti-duplicate controls, automatic workflows, governance parameters, and consolidated management views. It is based on the current BTP Prospecting implementation (Odoo 19).

---

## 1. Objectives & Scope

| Objective | What the system does |
|-----------|----------------------|
| **Security & consistency** | Restricted access by user, company, and role; logging of sensitive actions; audit trail (who, when, why). |
| **Hierarchical access** | N (base) sees own data; N-1 sees N-2 and below; Management has full access and assignment control. |
| **Data quality** | Anti-duplicates (clients/contacts, suppliers by SIREN, leads); duplicate alerts and optional force with N+1 notification. |
| **Automatic workflows** | Reminders (D0, D+15, D+30), document expiration alerts, automatic reattribution of inactive clients to manager. |
| **Governance** | Default parameters per service; documentary centralization; multi-company sharing rules; integrated messaging. |
| **Management view** | Consolidated group tables (CA by company/site, margins, cash); KPIs (conversion, yields, QHSE, reminders). |

---

## 2. How to Check Module 15 (Verification Steps)

Follow these steps to confirm that Module 15 is installed and working.

### 2.1 Install or upgrade the module

1. Log in as an administrator.
2. Go to **Apps**, search for **BTP Prospecting** (or your module name).
3. If the module is not yet installed, click **Install**. If it is already installed, click **Upgrade** so that Module 15 changes (new models, views, menus, cron) are applied.
4. Wait for the upgrade to finish, then reload the page if needed.

### 2.2 Quick checklist (menus and access)

Use a user who has **BTP Manager** or **BTP Administrator** rights.

| Step | What to do | What you should see |
|------|------------|----------------------|
| 1 | Open the main **BTP Prospecting** menu. | A **Governance** submenu appears (between Multi-companies and Configuration). |
| 2 | Click **Governance**. | Submenus: **Audit Log**, **Client Reattributions**, **Governance Reports**. |
| 3 | Click **Audit Log**. | A list (possibly empty). Columns: Date, User, Action, Model, Record ID, Reason. No Create button (read-only). |
| 4 | Click **Client Reattributions**. | A list of reattribution records (or empty). Columns include Partner, From, To, Changed By, Date, **Reason**. |
| 5 | Click **Governance Reports**. | List of report templates filtered to scopes **Data Quality** and **Reattributions**. You can create a template and run a report. |
| 6 | Go to **Settings → General Settings** (or **Settings** and open **BTP Prospecting** block). | A block **System Governance (Module 15)** with: **Enable automatic client reattribution** (checkbox), **Inactive client reattribution (days)** (number, e.g. 30). |
| 7 | Go to **Settings → Users & Companies → Users**, open a user. | In the BTP / preferences area: **System Governance** group with **Hierarchy Level** (read-only), **Temporary Rights**, and **From/To** dates. |

If all of the above are visible and behave as described, the Module 15 UI and menus are in place.

### 2.3 Trigger and check the Audit Log

1. **Reattribution**: Open **Clients & Contacts → Companies**, open a company that has an **Assigned salesperson**. Change the assigned salesperson and save.
2. Open **Governance → Audit Log**. You should see a new line: action **Reattribution**, model `res.partner`, and a reason describing the change.
3. **Force duplicate (optional)**: Create a **contact** (not company) with the same email as an existing contact; when warned, force duplicate. In **Governance → Audit Log** you should see an entry with action **Force Duplicate**.

### 2.4 Check Governance Reports

1. Go to **Governance → Governance Reports**.
2. Click **New**; set **Scope** to **Data Quality**; save; click **Run Report** (or equivalent). You should get a report with rows such as “Potential duplicate contacts”, “Suppliers with expired documents”, “Documentary conformity rate”.
3. Create another template with **Scope** = **Reattributions**, set optional **From/To** dates, run the report. You should see reattribution lines (or a message that there are none in the period).

### 2.5 Check automatic reattribution (optional)

1. In **Settings → BTP Prospecting → System Governance**, enable **Enable automatic client reattribution** and set **Inactive client reattribution (days)** to e.g. **30** (or 1 for a quick test if you can change the cron).
2. Ensure you have a **company** (client) with an **Assigned salesperson** whose **Manager** is set, and that this company has **not** been updated (no activity) for more than 30 days (or 1 day in the test).
3. Run the cron **BTP: Reattribute Inactive Clients to Manager** once (from **Settings → Technical → Automation → Scheduled Actions**, find it and click **Run Manually**), or wait for the daily run.
4. Check **Governance → Client Reattributions**: a new reattribution should appear (from the previous salesperson to the manager), with reason containing “Automatic reattribution”.
5. Check **Governance → Audit Log**: an entry with action **Reattribution** and the same reason.

### 2.6 Summary

- **Menus and settings** (section 2.2) confirm that Module 15 is loaded and visible.
- **Audit Log and Reattributions** (sections 2.3 and 2.5) confirm that logging and reattribution (including automatic) work.
- **Governance Reports** (section 2.4) confirm that Data Quality and Reattributions report scopes work.

For full acceptance scenarios (pyramidal access, duplicate alert, expired document, consolidated view), see **Section 11. Acceptance Scenarios** below.

---

## 3. Access Rights & Hierarchy

### 3.1 Hierarchical pyramid

- **N (Base)** — Salesperson / base employee: sees only **own** data (clients, leads, quotes).
- **N-2** — Has a manager (N-1); still sees only own data.
- **N-1** — Manager: sees **own + direct subordinates’** data (recursive: all N-2 under them).
- **Management** — BTP Manager / BTP Administrator: **full** access; assignment management.

Visibility is enforced by **record rules** on leads, and by **group membership** (BTP Salesperson, BTP Manager, BTP Administrator). The **Manager** field on the user (`Settings → Users`) defines the hierarchy; **Hierarchy Level** is computed (Base, N-2, N-1, Management).

### 3.2 Dynamic attributions

- **New employee**: Create user, set **Manager** and BTP groups; they get the correct level (N, N-2, N-1) and visibility.
- **Promotion / service change**: Change **Manager** and/or groups; hierarchy and visibility update.
- **Temporary rights**: On the user form, **Temporary Rights** + **From/To** dates can be used to document replacements or interim (reported in governance; access still follows groups and record rules).

**Where to configure**

- **BTP Prospecting** (or **Settings → Users**): **Manager**, **BTP Round-Robin**, **Temporary Rights** and dates, **Hierarchy Level** (read-only).

---

## 4. Data Security

| Feature | Implementation |
|--------|----------------|
| **Restricted access** | By user (record rules), company (multi-company rules), and role (BTP groups). |
| **Logging** | Sensitive actions are written to **Audit Log** (create/update/delete, reattribution, force duplicate). |
| **Audit trail** | Each reattribution stores **who** (Changed By), **when** (Change Date), **why** (Reason). Force-duplicate contact creation is logged and N+1 is notified. |
| **Backups** | Use your usual Odoo/PostgreSQL backup procedure (daily automatic backups and restore are not part of the addon). |
| **Sensitive data** | Passwords and session handling follow Odoo; store no sensitive secrets in plain text in the addon. |

**Where to consult**

- **BTP Prospecting → Governance → Audit Log**: list and form of all logged actions (user, action, model, record id, reason, date).

---

## 5. Anti-Duplicate Controls

### 5.1 Clients & contacts

- **Automatic search** on name, SIREN (companies), email, phone.
- **Duplicate alert** with indicated attribution (owner salesperson).
- **Force creation**: possible; **alert sent to N+1** (manager); **Audit Log** entry (force_duplicate).
- **Companies**: SIREN uniqueness enforced; no two companies with same SIREN.

### 5.2 Suppliers & subcontractors

- Search by name, SIREN/SIRET; enrichment via API when SIREN is provided.
- **Prohibition**: two company files with the same SIREN cannot be created (validation error).

### 5.3 Leads & opportunities

- **Duplicate detection** on (client + site) or (contact + project); duplicate flag and link to original.
- **Fusion**: Management can use the **Merge** action / wizard to merge duplicate leads.

---

## 6. Automatic Workflows

| Workflow | What happens |
|----------|--------------|
| **Client/prospect reminders** | D0, D+15, D+30 reminders and escalation to manager (configured crons and lead stages). |
| **Document expirations** | URSSAF, PV, TS, etc.: automatic alerts to salespeople and management; **subcontractor blocking** option (block operations when subcontractor documents are invalid). |
| **Automatic reattribution** | If enabled in **Settings → BTP Prospecting → System Governance**: clients with **no activity** for a configurable number of days are **reattributed to the salesperson’s manager**. Reason is recorded (“Automatic reattribution: no activity for X days”). |
| **Loyalty loops** | Reminders at 6 months for lost clients or completed sites (lead/site follow-up crons). |

**Where to configure**

- **Settings → BTP Prospecting**:  
  - **Subcontractors**: block when documents invalid; document expiration warning (days).  
  - **System Governance (Module 15)**: Enable automatic client reattribution; inactive client reattribution (days).

---

## 7. Modules Governance

- **Default parameters**: e.g. guarantee retention (e.g. 5%), forecast rate, document expiration days — in **Settings** and/or on relevant records (sites, products).
- **Documentary centralization**: Documents are attached to the right entities (partners, sites, articles); **Governance** and **Reports** give visibility (e.g. document conformity, expired docs).
- **Multi-companies**: Sharing rules (exclusive / shared / global) defined per company (**Multi-companies → Company Sharing Settings**).
- **Integrated messaging**: Emails, calls, appointments are attached to leads/partners via Odoo chatter and BTP modules (e.g. call reports, activities).

---

## 8. Management View & Global Piloting

- **Consolidated group tables**: **Multi-companies → Consolidation Reports** — CA by company, by site, global; actual vs forecast margins; consolidated cash (Module 13).
- **KPIs** (via reports and dashboards): quote-to-order conversion, site yields, invoicing delays, QHSE incidents, respect for commercial reminders.
- **Governance reports**: **Governance → Governance Reports** — scope **Data Quality** (duplicates, documentary conformity rate) and **Reattributions** (client reattribution history with who, when, why).

---

## 9. Data & Key Fields (Odoo)

| Object | Fields |
|--------|--------|
| **res.users** | `manager_id`, `subordinate_ids`, `all_subordinate_ids` (pyramid); `btp_hierarchy_level` (computed: base / n2 / n1 / management); `btp_temporary_rights`, `btp_temporary_rights_date_start`, `btp_temporary_rights_date_end`. |
| **btp.audit.log** | `user_id`, `action`, `model_name`, `res_id`, `reason`, `create_date`. |
| **btp.company.reattribution** | `partner_id`, `old_user_id`, `new_user_id`, `changed_by_id`, `change_date`, `reason`. |

---

## 10. Reports & KPI (Module 15)

| Report / KPI | Where | Content |
|--------------|--------|--------|
| **Data quality** | Governance → Governance Reports → Scope = Data Quality | Number of potential duplicate contacts; suppliers with expired documents; documentary conformity rate. |
| **Reattributions** | Governance → Governance Reports → Scope = Reattributions | List of reattributions (date, partner, from, to, by, reason). |
| **Hierarchical performance** | Lead/reminder reports and dashboards | Reminder follow-up by level (N / N-1) via lead and activity data. |
| **User follow-up** | Audit Log; Reattributions list | Connections (Odoo standard); sensitive actions and reattributions in Audit Log and Reattributions. |

---

## 11. Acceptance Scenarios

### S1 — Pyramidal access

- **Steps**: Log in as N-1 (manager). Open **Leads**.  
- **Expected**: You see **own** leads and **subordinates’** leads. Log in as N (salesperson): you see only **own** leads (and open/common as per rules). N does **not** see N-1’s data.

### S2 — Contact duplicate

- **Steps**: As salesperson, create a **contact** with same name/email/phone as an existing contact.  
- **Expected**: **Duplicate alert** with attribution (owner salesperson). If you **force creation**, N+1 is **notified** and an **Audit Log** entry (force_duplicate) is created.

### S3 — Expired document

- **Steps**: Use a **subcontractor** with an **expired URSSAF** (or equivalent) certificate; ensure **Block when subcontractor documents are invalid** is enabled.  
- **Expected**: **Automatic alert** (activity) on document expiration; **contract/site blocking** when the blocking option is enabled (site/document checks).

### S4 — Client reattribution

- **Steps**: Enable **automatic client reattribution**; set **inactive** days (e.g. 30). Have a client assigned to a salesperson with **no activity** for 30+ days and with the salesperson’s **Manager** set.  
- **Expected**: After the cron runs, the client is **reattributed to the manager**; **Reattributions** and **Audit Log** show who, when, and reason (“Automatic reattribution: no activity for X days”).

### S5 — Consolidated view

- **Steps**: As management, open **Multi-companies → Consolidation Reports**. Create/run reports for **Consolidated Turnover**, **Cash**, **Margin**; optionally filter by entity.  
- **Expected**: You see **multi-company consolidated** CA (and cash, margin); you can **drill down** by entity (company/site) via filters and report parameters.

---

## 12. Where to Find Everything (UI)

| Menu path | Content |
|-----------|--------|
| **BTP Prospecting → Governance → Audit Log** | All logged actions (user, action, model, record, reason, date). |
| **BTP Prospecting → Governance → Client Reattributions** | History of client/contact reattributions (partner, old/new user, changed by, date, reason). |
| **BTP Prospecting → Governance → Governance Reports** | Report templates scoped to **Data Quality** and **Reattributions**; run PDF/Excel/CSV. |
| **Settings → Users** (BTP section) | Manager, Hierarchy Level, Temporary Rights and dates. |
| **Settings → BTP Prospecting** | Subcontractor blocking; document expiration days; **System Governance**: automatic reattribution and inactive days. |
| **BTP Prospecting → Multi-companies** | Company sharing and consolidation (Module 13). |

---

## 13. AI / Automation (Proposal)

The documentation mentions **integrating AI to automate the maximum of tasks** from lead generation to exploitation. In the current implementation:

- **Automation** is in place via: reminders, escalations, document expiration alerts, automatic reattribution, and report scheduling.
- **AI-based automation** (e.g. lead scoring, auto-classification, predictive reattribution) would require additional development (external or Odoo AI/ML modules) and is **not** part of Module 15’s current deliverable. The architecture (clear hierarchy, audit log, reattribution history, and governance reports) is ready to support such extensions.

---

*End of Module 15 User & Testing Guide.*
