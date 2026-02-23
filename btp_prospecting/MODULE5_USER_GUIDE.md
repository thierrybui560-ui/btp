## BTP Prospecting (Module 5) — Sites & Documents Management

This guide provides step-by-step instructions with complete mock data for Module 5.
It follows the same structure and demo users as Module 1, 2, 3, and 4.

---

## Table of Contents

1. [Where to Find Module 5 in the UI](#1-where-to-find-module-5-in-the-ui)
2. [Prerequisites and Mock Users](#2-prerequisites-and-mock-users)
3. [Configuration (Document Expiration Warning)](#3-configuration-document-expiration-warning)
4. [Site Creation from Accepted Quote](#4-site-creation-from-accepted-quote)
5. [Manual Site Creation](#5-manual-site-creation)
6. [Document Categories & Attachment](#6-document-categories--attachment)
7. [Multi-Entity Linking (Site + Supplier + Subcontractor + Item)](#7-multi-entity-linking-site--supplier--subcontractor--item)
8. [Versioning & Archiving](#8-versioning--archiving)
9. [Checklist & Mandatory Documents](#9-checklist--mandatory-documents)
10. [Stakeholders & Internal Teams](#10-stakeholders--internal-teams)
11. [Workflow & Automations](#11-workflow--automations)
12. [Reports & KPIs](#12-reports--kpis)
13. [Acceptance Scenarios S1–S5](#13-acceptance-scenarios-s1–s5)
14. [Quick Mock Dataset (Copy/Paste)](#14-quick-mock-dataset-copypaste)
15. [Troubleshooting](#15-troubleshooting)

---

## 1) Where to Find Module 5 in the UI

Navigation:
- **BTP Prospecting → Sites & Documents → Sites** (list of sites; open a site to see its form with tabs: Documents, Checklist, Stakeholders, Contracts, Technical Documents, Safety, etc.)
- **BTP Prospecting → Sites & Documents → Site Documents**
- **BTP Prospecting → Sites & Documents → Site Reports**

If not visible:
- Ensure your user has **BTP Salesperson**, **BTP Manager**, or **BTP Administrator** group.
- Logout and login again to refresh menus.

---

## 2) Prerequisites and Mock Users

Use the same demo users as Module 1–4:
- Alice Martin (Salesperson, BTP France)
- Bernard Leroy (Salesperson, BTP France)
- Emma Petit (Salesperson, BTP Belgium)
- David Roche (Manager, BTP France)

Prerequisites:
- A client company exists (Module 2).
- A quote exists and can be accepted (Module 3).
- Subcontractors and suppliers exist (Module 4).

---

## 3) Configuration (Document Expiration Warning)

Navigation: **Settings → General Settings → BTP Prospecting**

Settings:
- **Block when subcontractor documents are invalid**: ✅ (optional)
- **Document expiration warning (days)**: `30`

This setting controls:
- Expiration warning threshold for site documents.

---

## 4) Site Creation from Accepted Quote

Goal: Accept a quote to generate a site automatically.

Navigation: **BTP Prospecting → Quotes & Articles → Quotes**

Steps:
1. Open a quote (e.g., `202501001`).
2. Click **Confirm** to accept the quote.
3. Open the quote again and check the **Site** field.

Expected:
- A new **Site** is created automatically.
- A **Site Code** is generated in format `YYYYMMNNN`.

---

## 5) Manual Site Creation

Navigation: **BTP Prospecting → Sites & Documents → Sites**

Steps:
1. Click **Create**.
2. Fill the fields:
   - **Site Code**: auto (leave empty)
   - **Site Name**: `Tour La Défense – Flocking`
   - **Client**: `BTP France SA`
   - **Site Manager**: `David Roche`
   - **Start Date**: `2026-03-01`
   - **Planned End Date**: `2026-06-30`
   - **Address**: `12 Rue de la Paix, Paris`
3. Save.

Expected:
- Site appears in list with a unique code.

---

## 6) Document Categories & Attachment

Document Categories:
1. **Contracts** (client contract, subcontractor contracts, amendments)
2. **Regulatory** (PPSPS, DIUO, authorizations, safety certificates)
3. **Technical** (plans, DOE, article notices)
4. **Supplier/Subcontractor** (delivery notes, certificates)
5. **Miscellaneous** (photos, meeting minutes, PV)

Navigation: **Sites & Documents → Sites** → (open a site) → **Documents** tab

Steps:
1. Add a document:
   - **Category**: `Regulatory`
   - **Type**: `PPSPS`
   - **Name**: `PPSPS Site V1`
   - **Issue Date**: `2026-02-15`
   - **Expiration Date**: `2026-12-31`
   - **Attachment**: upload PDF
2. Save.

Expected:
- Document appears in the **Safety** tab (same form; shows Regulatory documents) and in the general **Documents** list.

---

## 7) Multi-Entity Linking (Site + Supplier + Subcontractor + Item)

Navigation: **Sites & Documents → Sites** → (open a site) → **Documents** tab (or **Technical Documents** tab)

Steps:
1. Create a technical plan and link it:
   - **Category**: `Technical`
   - **Type**: `Plan`
   - **Name**: `Fireproofing Plan A`
   - **Supplier**: `ThermoSafe Supplies`
   - **Subcontractor**: `Flocage Pro`
   - **Quote Item**: `Application flocking thickness 3 cm`
2. Save.

Expected:
- Document is linked to multiple entities and visible from the site.

---

## 8) Versioning & Archiving

Steps:
1. Create a new version of the same document:
   - Same **Name** and **Type**
   - The system assigns **Version = 2**
2. Save.

Expected:
- Old version is automatically **archived** (still viewable).
- The newest version is marked as the **latest**.

---

## 9) Checklist & Mandatory Documents

Navigation: **Sites & Documents → Sites** → (open a site) → **Checklist** tab

Steps:
1. Add a requirement:
   - **Category**: `Regulatory`
   - **Type**: `PPSPS`
   - **Mandatory**: ✅
   - **Required Before Start**: ✅
2. Save.

Expected:
- The checklist shows **Missing = True** until a valid PPSPS is attached.
- The site shows **Blocked = True** if mandatory documents are missing/expired.

---

## 10) Stakeholders & Internal Teams

Navigation: **Sites & Documents → Sites** → (open a site) → **Stakeholders** tab

**Prerequisites (must exist in your database):**
- **Client Contacts** — a *contact* (person, not company), e.g. **Alice Martin**. Create in **Contacts** or use an existing contact.
- **Subcontractors** — a *company* with **Subcontractor** checked, e.g. **Flocage Pro**. Create in **Quotes & Articles → Subcontractors** (or on the partner form: BTP Supplier/Subcontractor tab, set as Subcontractor).
- **Suppliers** — a *company* with **Supplier** checked, e.g. **ThermoSafe Supplies**. Create in **Quotes & Articles → Suppliers** (or on the partner form: set as Supplier).
- **Assigned Employees** — an *internal user*, e.g. **Bernard Leroy**. Must exist in **Settings → Users & Companies → Users** (Odoo user, not only a contact).

If a name does not appear in the dropdown, create the record with the correct type and flag first, then come back to the site’s Stakeholders tab.

Add:
- **Client Contacts**: `Alice Martin`
- **Subcontractors**: `Flocage Pro`
- **Suppliers**: `ThermoSafe Supplies`
- **Assigned Employees**: `Bernard Leroy`

Save the site form.

Expected:
- Stakeholders are visible directly on the site file (same tab shows the tags/names after save; re-opening the site shows them again).
- **Check:** Open the site → **Stakeholders** tab → the four fields show the selected names. Leave and re-open the site to confirm they are stored.

---

## 11) Workflow & Automations

Automations included:
- **Automatic site creation** from accepted quote.
- **Expiration reminders** for site documents.
- **Blocking indicator** when mandatory documents are missing/expired.

Expected:
- Expiring documents create activities for the site manager.

---

## 12) Reports & KPIs

Only **two** of the three KPIs below are in **Site Documents Analysis**; **Delayed sites** is on the **Sites** list (different screen).

**Site Documents Analysis** (document counts and filters)

Navigation: **Sites & Documents → Site Reports → Site Documents Analysis**

- Opens a **pivot** (count of documents by Site × Category × Type) and **list** view of site documents.
- **Missing/expired documents by site:**  
  In the list view, use the **Expired** or **Expiring Soon** filter, then **Group By → Site** to see expired/expiring documents per site.  
  To see *sites* that have missing mandatory documents or expired docs, use **Sites & Documents → Sites** and apply the **Missing Documents** or **Expired Documents** filter.
- **Contract history by site:**  
  In Site Documents Analysis, apply the **Contracts** filter (category = Contracts), then use **Group By → Site** or the pivot (rows = Site) to see contract documents by site.

**Delayed sites** (not in Site Documents Analysis — use Sites list)

Navigation: **Sites & Documents → Sites** (not Site Reports)

- Open the **Sites** list, then apply the **Delayed** filter to see sites where **Planned End Date &lt; today** and **Actual End Date** is not set.

---

## 13) Acceptance Scenarios S1–S5

S1 — Site creation:
- Accepted quote generates site `Tour La Défense – Flocking`
- Site code: `202501001`

S2 — Missing PPSPS:
- Checklist shows PPSPS missing
- Site blocked indicator enabled

S3 — Subcontractor certificate expired:
- Subcontractor document expires
- Site document expiration warning triggers reminder

S4 — Multi-entity attachment:
- Technical plan attached to site + supplier + subcontractor + item

S5 — Site closure:
- Set **Actual End Date**
- DOE generated by collecting technical documents

---

## 14) Quick Mock Dataset (Copy/Paste)

Site:
- **Name**: `Tour La Défense – Flocking`
- **Client**: `BTP France SA`
- **Manager**: `David Roche`
- **Start Date**: `2026-03-01`
- **Planned End Date**: `2026-06-30`
- **Address**: `12 Rue de la Paix, Paris`

Documents:
1. `PPSPS Site V1` — Regulatory → PPSPS — expires `2026-12-31`
2. `Fireproofing Plan A` — Technical → Plan
3. `Subcontractor Contract` — Contracts → Subcontractor Contract

Checklist:
- PPSPS (Mandatory ✅, Required Before Start ✅)
- Client Contract (Mandatory ✅)
- DOE (Mandatory ☐)

---

## 15) Troubleshooting

**Problem:** Site not created from accepted quote  
**Solution:** Check that the quote is in **Sale** state and not still draft.  

**Problem:** Document not marked as expiring soon  
**Solution:** Check **Settings → BTP Prospecting → Document expiration warning (days)**.  

**Problem:** Site blocked but documents are present  
**Solution:** Ensure the latest document version is active and not expired.  

**Problem:** Menu “Sites & Documents” not visible  
**Solution:** Check user access rights (BTP Salesperson/Manager/Admin).  
