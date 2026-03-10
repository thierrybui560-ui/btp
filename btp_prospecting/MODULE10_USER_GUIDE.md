# Module 10 - Quality & Safety (QHSE)

## Detailed Functional Guide + Full UAT Playbook (Odoo 19)

This guide is an execution-ready UAT manual for Module 10.
It is written for key users, project managers, QHSE managers, and testers.

---

## 1) Objective and Scope

Module 10 covers:

- QHSE incident declaration and workflow (incident, accident, near miss, non-conformity).
- Corrective action planning, assignment, and closure traceability.
- QHSE documentary linkage through Site Documents (PPSPS, certificates, PV, technical sheets, DOE).
- Site-centered visibility and KPI reporting.

The module works together with Site Documents features from Module 5.

---

## 2) Requirement-to-Implementation Check (Module 10)


| Requirement                                                   | Status                 | Current implementation in project                                                  |
| ------------------------------------------------------------- | ---------------------- | ---------------------------------------------------------------------------------- |
| QHSE incidents declaration with type/date/description/site    | Implemented            | `btp.qse.incident` model + list/form + site integration                            |
| Mobile declaration with photo                                 | Implemented            | `/btp/mobile/incident/create` endpoint with optional photo                         |
| Workflow New -> In Progress -> Closed                         | Implemented            | Actions: Assign to me, Close, Reopen                                               |
| Validation by QHSE responsible                                | Implemented (hardened) | Close now requires responsible user (or manager/admin)                             |
| Corrective actions with assignee/deadline/status              | Implemented            | `btp.qse.corrective.action` one2many on incident                                   |
| Closure only after corrective actions verified                | Implemented (hardened) | Close blocked if open corrective actions remain                                    |
| Site documentary management (PPSPS, certificates, PV, DOE)    | Implemented            | `btp.site.document` with categories/types/version/validity                         |
| Versioning and archive old versions                           | Implemented            | New version auto-archives previous versions (`active=False`)                       |
| Validity date alerts                                          | Implemented            | Cron creates activities for expiring/expired docs                                  |
| Link document to site/supplier/subcontractor/article          | Implemented (hardened) | Added `article_id` on site document                                                |
| Reports/KPI incidents by type/frequency/site                  | Implemented            | Pivot/graph/list on incidents + report template scope                              |
| Multi-company isolation for QHSE records                      | Implemented (hardened) | Global company rules for incidents/actions/documents                               |
| Auto PDF technical dossier with ToC and DOE conversion engine | Partial                | Document storage exists; full automated dossier assembly is not a dedicated engine |


---

## 3) Menus and Navigation

Main paths:

- `BTP Prospecting -> Sites & Documents -> Quality & Safety (QHSE) -> Incidents`
- `BTP Prospecting -> Sites & Documents -> Sites -> [Open Site] -> Quality & Safety (QHSE) tab`
- `BTP Prospecting -> Sites & Documents -> Site Documents`
- `BTP Prospecting -> Sites & Documents -> Site Reports`

Related standard paths:

- `Inventory -> Operations -> Physical Inventory` (for stock-linked document tests if needed)
- `Settings -> Technical -> Scheduled Actions` (admin-only cron verification)

---

## 4) Test Roles and Prerequisites

## 4.1 Roles

- QHSE tester: BTP Salesperson or Manager.
- Validation tester: BTP Manager/Admin.
- Optional mobile tester: user with API session access.

## 4.2 Mandatory base data

Create or verify:

1. Site: `Tour La Defense - Flocking` with a valid Site Code.
2. Users:
  - `worker_user` (reporting user),
  - `qhse_user` (responsible),
  - `manager_user` (manager/admin).
3. Site Documents examples:
  - PPSPS V1
  - Safety certificate
  - Conformity PV
  - DOE
4. One BTP article (product template) for technical docs linkage.

---

## 5) Field Map (Core Objects)

## 5.1 Incident (`btp.qse.incident`)

- `name` (reference), `site_id`, `date`, `description`
- `incident_type` (incident/accident/near_miss/non_conformity)
- `severity` (low/medium/high/critical)
- `state` (new/in_progress/closed)
- `responsible_id`
- `attachment_ids`
- `corrective_action_ids`

## 5.2 Corrective action (`btp.qse.corrective.action`)

- `incident_id`, `site_id`, `company_id`
- `name`, `assigned_to_id`, `deadline`, `state`, `done_date`

## 5.3 Site document (`btp.site.document`)

- `site_id`, `company_id`, `category`, `document_type`, `name`
- `version`, `version_label`, `active`
- `issue_date`, `expiration_date`, `is_expired`, `expires_soon`
- `supplier_id`, `subcontractor_id`, `article_id`, `quote_id`, `quote_item_id`

---

## 6) Acceptance Scenarios (Detailed)

---

## S1 - PPSPS versioning and archival

### Goal

Validate PPSPS lifecycle: V1 creation, V2 update, V1 archival.

### Preconditions

- Site exists with Site Code.
- User can create Site Documents.

### Steps

1. Open `BTP Prospecting -> Sites & Documents -> Sites`.
2. Open site `Tour La Defense - Flocking`.
3. Go to `Safety` tab (or `Site Documents` menu).
4. Create document:
  - Category = `Regulatory`
  - Type = `PPSPS`
  - Name = `PPSPS - Tour La Defense`
  - Issue date = today
  - Version (leave default for first creation)
5. Save (this is V1).
6. Create second record with same Site + Type + Name for V2.
7. Save.
8. Filter by Name and review both versions.

### Expected

- New record gets next version label (`V2`).
- Previous version is archived (`active=False`) and still consultable.

### Evidence

- Screenshot list showing V1 and V2.
- Screenshot V1 inactive + V2 active.

### Failure checks

- Version not incremented: verify same Site + Type + Name grouping.
- Old version not archived: confirm creation via new record (not overwrite).

---

## S2 - Mobile incident declaration + validation + corrective action

### Goal

Validate incident can be declared with photo, validated by responsible, and closed after corrective action.

### Preconditions

- Incident reporter user and QHSE responsible user exist.
- Site exists and visible to reporting user.

### Steps (Web flow equivalent)

1. Open `Quality & Safety (QHSE) -> Incidents -> New`.
2. Set:
  - Site = `Tour La Defense - Flocking`
  - Type = `Incident`
  - Severity = `High`
  - Description = test description
  - Location / Concerned Team = optional
3. Save.
4. In `Photos / Attachments` section, drag and drop photo(s) or click to browse and upload file(s).
5. Click `Assign to me` as QHSE responsible (or set responsible).
6. In `Corrective Actions` tab add one action:
  - Action name
  - Assigned to
  - Deadline
7. Mark corrective action `Done`.
8. Click `Close`.

### Optional API check (mobile endpoint)

- Route: `/btp/mobile/incident/create`
- Payload includes `site_id`, `description`, `incident_type`, optional `severity`, `concerned_team`, `photo_base64`.

### Expected

- Incident created with reference.
- Status transition works (New -> In Progress -> Closed).
- Close is blocked until:
  - responsible is defined,
  - all corrective actions are done.

### Evidence

- Incident form with severity and status.
- Corrective action line done.
- Closed incident with closed date.

### Failure checks

- Cannot close: expected if open corrective actions remain.
- Cannot close: expected if responsible missing.

---

## S3 - PV expiration alert (30 days before due date)

### Goal

Validate expiration alert mechanism for conformity PV.

### Preconditions

- Scheduled action for document expiration check is active.

### Steps

1. Open Documents tab in Site `Site Documents`.
2. Create document:
  - Category = `Regulatory` or `Technical` (per process)
  - Type = `Conformity PV`
  - Name = `PV Test`
  - Expiration date = today + 30 days
3. Save.
4. Trigger cron manually (admin) or wait schedule:
  - scheduled action linked to document expiration check.
5. Open site related activities.

### Expected

- Activity is created for expiring document.
- If date passes, expired activity message is generated.

### Evidence

- Document with expiration date.
- Generated activity on site.

### Failure checks

- No activity: verify cron active and activity type exists.
- Wrong assignee: verify site manager/user on site.

---

## S4 - Technical dossier structure check

### Goal

Validate technical document organization by site/article/supplier/subcontractor and retrieval by filters.

### Preconditions

- At least one BTP article exists.

### Steps

1. Open `Site Documents -> New`.
2. Create technical sheet record:
  - Category = `Technical`
  - Type = `Article Notice` or `Conformity PV`
  - Site = target site
  - Article = selected BTP article
  - Optional supplier/subcontractor links
3. Save.
4. Open site `Technical Documents` tab and verify row appears.
5. Use search/group in Site Documents:
  - Group by Type / Site
  - Filter by Article

### Expected

- Document is classifiable and retrievable by site and category.
- Article link is stored and visible.

### Evidence

- Site technical tab with linked article.
- Global list grouped/filtered output.

### Failure checks

- Article field empty from dropdown: verify article flagged as BTP article.

---

## S5 - DOE end-of-site documentary trace

### Goal

Validate DOE record creation/versioning and end-of-site documentary traceability.

### Preconditions

- Site has at least one technical/regulatory document.

### Steps

1. Open `Site Documents -> New`.
2. Create DOE:
  - Category = `Technical`
  - Type = `DOE`
  - Name = `DOE - Tour La Defense`
  - Add attachment (compiled file or placeholder)
3. Save.
4. Create DOE V2 record with same name/type/site.
5. Save and verify archive/version behavior.

### Expected

- DOE is versioned and old version archived.
- DOE remains visible in technical dossier trace.

### Evidence

- DOE V1/V2 records and active flags.
- Attachment evidence on latest DOE.

### Failure checks

- Missing DOE type: verify module upgraded with latest document types.

---

## 7) Extended Operational Scenarios

## S6 - Incident KPI (type/frequency/severity)

- Open `QHSE -> Incidents` in pivot/graph.
- Group by Type + Severity + Site + Date.
- Verify counts match created UAT incidents.

## S7 - Site-centric access

- From site form, use `Incidents` stat button and QHSE tab.
- Verify only site incidents are shown.

## S8 - Multi-company segregation

- Create incidents/documents in Company A.
- Switch to Company B context.
- Verify records are isolated by company rules.

---

## 8) Reports & KPI Validation Checklist

- Incident list supports filtering by status/type/severity/site.
- Incident pivot/graph displays site/type trends.
- Missing/expired document follow-up visible from site/checklist.
- Documentary conformity logic (complete vs missing/expired) is testable per site.
- DOE records are traceable with version history.

---

## 9) Troubleshooting Matrix


| Symptom                             | Likely cause              | Check                                             |
| ----------------------------------- | ------------------------- | ------------------------------------------------- |
| Site not selectable on incident     | Site has no code          | Ensure `btp_site_code` set                        |
| Cannot close incident               | Workflow guardrail active | Set responsible + complete all corrective actions |
| No expiration alerts                | Cron/config issue         | Check scheduled action and activity type          |
| Article not selectable in documents | Product setup issue       | Ensure product template has `is_btp_article=True` |
| Cross-company records visible       | Missing upgrade           | Upgrade module to load company record rules       |


---

## 10) What Was Hardened in This Revision

The following module fixes were applied during this review:

- Added incident `severity` field and UI/search coverage.
- Enforced close workflow controls:
  - responsible required,
  - only responsible or manager/admin can close,
  - all corrective actions must be done before closure.
- Added `article` linkage on site documents for technical/QHSE documents.
- Extended mobile incident API payload to support severity and concerned team.
- Added multi-company record rules for:
  - QHSE incidents,
  - corrective actions,
  - site documents.
- Added `Conformity PV` document type for regulatory traceability.

---

## 11) Final Acceptance Form (Module 10)

Tester:

Company:

Environment:

Date:

Scenarios executed (S1-S5 mandatory, S6-S8 recommended): PASS / FAIL / BLOCKED

Open defects:

Decision:

- GO
- CONDITIONAL GO
- NO GO

