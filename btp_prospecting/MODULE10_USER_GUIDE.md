# Module 10 — Quality & Safety (QHSE) — User & Testing Guide

This guide helps you **test Module 10 manually**: where to find QHSE features, how to declare and manage incidents, and how they integrate with sites. It is based on the current BTP Prospecting implementation (Odoo 19).

---

## 1. What Module 10 Does (Summary)


| Goal                             | What the system does                                                                                                                                                                           |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **QHSE documents**               | PPSPS, regulatory certificates, conformity PV, technical sheets, DOE: managed in **Site Documents** (Module 5) with categories Safety/Regulatory/Technical, versioning, and expiration alerts. |
| **Incidents & non-conformities** | Declare incidents, accidents, near misses, non-conformities per site; attach photos; assign QHSE responsible; track status (New → In Progress → Closed).                                       |
| **Corrective actions**           | Link corrective actions to each incident (description, assignee, deadline); mark done; history preserved.                                                                                      |
| **Site integration**             | Each incident is linked to one BTP site; from the site form you see the **Quality & Safety (QHSE)** tab and an **Incidents** stat button.                                                      |
| **Traceability**                 | Chatter and activities on incidents; all (re)attributions and closures are tracked.                                                                                                            |


**Note:** QHSE **documentary** management (PPSPS, DOE, certificates, validity dates, alerts) is already implemented in **Sites & Documents** via **Site Documents** and **Document Checklist**. Module 10 adds **Incidents** and **Corrective Actions** on top of that.

---

## 2. Feature List (What You Can Test)


| #   | Feature                                                                            | Where to test                                            | Section |
| --- | ---------------------------------------------------------------------------------- | -------------------------------------------------------- | ------- |
| F1  | **Create QHSE incident** — Site, date, type, description, optional location/team   | Quality & Safety (QHSE) → Incidents → New                | 5.1     |
| F2  | **Attach photos** — Photos/documents on incident                                   | Incident form → Photos / Attachments                     | 5.2     |
| F3  | **Assign to me** — QHSE responsible takes the incident (New → In Progress)         | Incident form → Assign to me                             | 5.3     |
| F4  | **Corrective actions** — Add actions with assignee and deadline; Mark done         | Incident form → Corrective Actions tab                   | 5.4     |
| F5  | **Close incident** — Close with optional internal notes                            | Incident form → Close                                    | 5.5     |
| F6  | **Incidents from site** — Create/view incidents from site form (tab + stat button) | Sites → [Site] → Quality & Safety tab / Incidents button | 5.6     |
| F7  | **Filters & groups** — By status, type, site                                       | Incidents list → filters / group by                      | 6       |
| F8  | **Site documents (QHSE)** — PPSPS, safety, technical docs (existing)               | Sites → [Site] → Documents / Safety / Technical          | 4       |


---

## 3. Where to Find Everything (UI Navigation)

### 3.1 BTP menu: Quality & Safety (QHSE)


| Menu path                                                                                   | What you see                           | Access           |
| ------------------------------------------------------------------------------------------- | -------------------------------------- | ---------------- |
| **BTP Prospecting → Sites & Documents → Quality & Safety (QHSE) → Incidents**               | All QHSE incidents (list/form).        | BTP Salesperson+ |
| **BTP Prospecting → Sites & Documents → Quality & Safety (QHSE) → Incidents → New**         | Incidents with status **New**.         | BTP Salesperson+ |
| **BTP Prospecting → Sites & Documents → Quality & Safety (QHSE) → Incidents → In Progress** | Incidents with status **In Progress**. | BTP Salesperson+ |


### 3.2 From a site


| Where                                                                         | What                                                                         |
| ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **Sites & Documents → Sites** → open a site → **Quality & Safety (QHSE)** tab | Inline list of incidents for this site; create new from here.                |
| Same site form → **Incidents** stat button (top right)                        | Opens list of incidents filtered by this site.                               |
| Same site form → **Documents** / **Safety** / **Technical Documents** tabs    | QHSE-related documents (PPSPS, certificates, DOE, etc.) — existing Module 5. |


### 3.3 Access rights

- **Incidents**, **Corrective actions**: BTP Salesperson can read/create/edit (no delete); BTP Manager and Admin can delete.  
- **Site Documents** (including PPSPS, safety): same as Module 5 (Salesperson read/write/create; Manager/Admin full).

---

## 4. QHSE Documents vs Incidents


| Need                                                         | Use                                      | Location                                                           |
| ------------------------------------------------------------ | ---------------------------------------- | ------------------------------------------------------------------ |
| PPSPS, certificates, DOE, technical sheets, validity, alerts | **Site Documents**                       | Site form → Documents / Safety / Technical Documents               |
| Incident, accident, near miss, non-conformity declaration    | **QHSE Incidents** (Module 10)           | Quality & Safety (QHSE) → Incidents or Site → Quality & Safety tab |
| Corrective actions following an incident                     | **Corrective Actions** (inside incident) | Incident form → Corrective Actions tab                             |


---

## 5. Step-by-Step Tests

### 5.1 Create a QHSE incident (F1)

**Steps**

1. **BTP Prospecting → Sites & Documents → Quality & Safety (QHSE) → Incidents** → **New**.
2. **Site** = a BTP site with a site code (e.g. Tour La Défense – Flocking).
3. **Date** = today (or incident date).
4. **Type** = Incident / Accident / Near Miss / Non-Conformity.
5. **Description** = e.g. "Trip hazard at entrance; barrier missing."
6. Optionally: **Location on Site**, **Concerned Team**.
7. Save.

**Expected**

- **Reference** is auto-generated (e.g. QSE-00001).  
- **Status** = New.  
- **Reported By** = current user.

### 5.2 Attach photos (F2)

**Steps**

1. Open the incident created above.  
2. Find the **Chatter** panel: it is the **right-hand panel** of the form (sometimes collapsed as a narrow strip with a message icon). **Click the panel or the message/activity icon** to expand it if needed.  
3. In the expanded Chatter you’ll see the activity log, a message box, and an **attachment area**. **Drag and drop** files into that area, or click to browse. You can also type a note and attach files when posting.  
4. Save if needed (posting an attachment usually auto-saves).

**Expected**

- Attachments appear in the **Photos / Attachments** section above and in the Chatter; they are stored on the incident (same list in both places).

### 5.3 Assign to me (F3)

**Steps**

1. Open an incident in status **New**.
2. Click **Assign to me** in the header.
3. Save (or let it auto-save).

**Expected**

- **QHSE Responsible** = current user.  
- **Status** = In Progress.  
- Button **Assign to me** disappears.

### 5.4 Corrective actions (F4)

**Steps**

1. Open an incident (New or In Progress).
2. Go to the **Corrective Actions** tab.
3. **Add a line**: Action = "Install barrier at entrance", Assigned To = a user, Deadline = a future date, Status = Open.
4. Save.
5. Later: open the same incident, go to Corrective Actions, and click **Mark done** on the action (or set Status = Done).

**Expected**

- **Corrective Actions** count visible on the incident list and on the site’s QHSE tab.  
- **Mark done** sets Status = Done and **Done Date** = today.  
- **Reopen** on an action sets it back to Open.

### 5.5 Close incident (F5)

**Steps**

1. Open an incident in status **New** or **In Progress**.
2. Optionally add **Internal Notes** in the Notes tab.
3. Click **Close** in the header.
4. Save.

**Expected**

- **Status** = Closed.  
- **Closed Date** = today.  
- **Reopen** button appears; clicking it sets Status back to In Progress and clears Closed Date.

### 5.6 Incidents from site (F6)

**Steps**

1. **Sites & Documents → Sites** → open a site (e.g. Tour La Défense – Flocking).
2. Click the **Incidents** stat button (top right; shows count if > 0).
3. Or open the **Quality & Safety (QHSE)** tab and click **New** in the incidents list (with **Site** defaulted to current site).
4. Create an incident; return to the site form.

**Expected**

- **Incidents** count updates.  
- **Quality & Safety (QHSE)** tab shows the new incident in the list.

---

## 6. Filters & Group By (F7)

**Steps**

1. **Quality & Safety (QHSE) → Incidents**.
2. Use **Filters**: New, In Progress, Closed; or Accident, Non-Conformity.
3. Use **Group By**: Site, Type, Status.

**Expected**

- List updates; grouping shows counts per site/type/status.

---

## 7. Acceptance Scenarios (Spec Module 10)

Use a BTP site with a site code (e.g. Tour La Défense – Flocking).

### S1 — PPSPS (Site Documents)

1. **Sites** → open site → **Documents** or **Safety** tab.
2. Add a document: Category = Regulatory, Type = PPSPS, Name = "PPSPS V1", Version, Issue/Expiration dates.
3. Edit and save again with a new version label → **PPSPS V2**; previous version remains in history.
4. **Verify**: Document appears in Safety/Regulatory; expiration alerts via existing cron (Module 5).

### S2 — Mobile incident (declaration + corrective action)

1. **Quality & Safety (QHSE) → Incidents** → **New**.
2. Site = Tour La Défense – Flocking, Type = Incident, Description = "Worker reported fall risk on stairwell", attach a photo if available.
3. Save → **Assign to me** → Status = In Progress.
4. **Corrective Actions** tab → Add: "Install handrail", Assigned To = [user], Deadline = [date].
5. **Mark done** on the action; then **Close** the incident.
6. **Verify**: Incident closed; corrective action Done; history in chatter.

### S3 — PV expiration (Site Documents)

1. **Site Documents** (or Site → Safety): add document Type = Conformity PV, set **Expiration Date** = 30 days from now.
2. **Verify**: Existing document expiration cron creates activities (expiring soon / expired) as in Module 5.

### S4 — Technical dossier (Site Documents)

1. **Site** → **Technical Documents** tab: add documents (TS, DOE, notices) linked to the site (and optionally to supplier/article).
2. **Verify**: Documents listed by category; versioning and dates as in Module 5.
3. (Full technical dossier PDF generation / DOE export can be a future extension.)

### S5 — DOE at end of site (Site Documents)

1. **Site** → **Documents** or **Technical Documents**: add document Type = DOE, with version and dates.
2. **Verify**: DOE stored and versioned like other site documents; end-of-site archiving uses existing document logic.

---

## 8. Troubleshooting


| Problem                                        | What to check                                                                                                                          |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Incidents menu not visible**                 | User must have BTP Prospecting access (e.g. BTP Salesperson, Manager, or Admin).                                                       |
| **Site dropdown empty when creating incident** | Only **projects with a Site Code** appear; create the site from a quote ("Create site") or set **Site Code** on the project.           |
| **Reference shows "New"**                      | Sequence **btp.qse.incident** must be installed: upgrade the module or check **Settings → Technical → Sequences** for "QHSE Incident". |
| **Cannot delete incident**                     | Only BTP Manager or Admin can delete; Salesperson has no delete right.                                                                 |
| **Corrective action "Mark done" does nothing** | Ensure you are on the Corrective Actions tab and the line status is Open; button is per line.                                          |
| **QHSE documents (PPSPS, DOE)**                | Use **Site Documents** (Site form → Documents / Safety / Technical), not the Incidents menu.                                           |
| **Can't find Chatter / drag and drop for photos** | The Chatter is the **right-hand panel** on the incident form. If you only see a narrow strip, click it to expand. Scroll inside the Chatter to see the message box and attachment area where drag and drop works. |


---

## 9. Quick Reference — Key Fields


| Model                         | Field                  | Meaning                                           |
| ----------------------------- | ---------------------- | ------------------------------------------------- |
| **btp.qse.incident**          | name                   | Auto reference (e.g. QSE-00001).                  |
| **btp.qse.incident**          | site_id                | BTP site (project with site code).                |
| **btp.qse.incident**          | date                   | Incident date.                                    |
| **btp.qse.incident**          | incident_type          | incident / accident / near_miss / non_conformity. |
| **btp.qse.incident**          | state                  | new / in_progress / closed.                       |
| **btp.qse.incident**          | user_id                | Reported by.                                      |
| **btp.qse.incident**          | responsible_id         | QHSE responsible (set via "Assign to me").        |
| **btp.qse.incident**          | attachment_ids         | Photos/documents.                                 |
| **btp.qse.incident**          | corrective_action_ids  | One2many to corrective actions.                   |
| **btp.qse.corrective.action** | incident_id            | Parent incident.                                  |
| **btp.qse.corrective.action** | name                   | Action title.                                     |
| **btp.qse.corrective.action** | assigned_to_id         | User responsible for the action.                  |
| **btp.qse.corrective.action** | deadline               | Due date.                                         |
| **btp.qse.corrective.action** | state                  | open / done.                                      |
| **project.project**           | btp_qse_incident_ids   | Incidents linked to the site.                     |
| **project.project**           | btp_qse_incident_count | Number of incidents (for stat button).            |


---

## 10. Summary Checklist

- QHSE **documents** (PPSPS, certificates, DOE, technical) are managed in **Site Documents** (Documents / Safety / Technical tabs).  
- **Incidents** are created from **Quality & Safety (QHSE) → Incidents** or from the site form (**Quality & Safety** tab or **Incidents** stat button).  
- Each incident has **Type**, **Status**, optional **Location** / **Concerned Team**, and **Photos/Attachments**.  
- Use **Assign to me** to take ownership and set status to In Progress.  
- **Corrective Actions** are defined on the incident form; they can be marked Done and the incident can be Closed.  
- Only projects with a **Site Code** appear in the Site field of incidents.

