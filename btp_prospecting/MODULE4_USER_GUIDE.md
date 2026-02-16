## BTP Prospecting (Module 4) — Subcontractors Management

This guide provides step-by-step instructions with complete mock data for Module 4.
It follows the same structure and demo users as Module 1, 2, and 3.

---

## Table of Contents

1. [Where to Find Module 4 in the UI](#1-where-to-find-module-4-in-the-ui)
2. [Prerequisites and Mock Users](#2-prerequisites-and-mock-users)
3. [Configuration (Blocking + Expiration Alerts)](#3-configuration-blocking--expiration-alerts)
4. [Subcontractor Creation via API](#4-subcontractor-creation-via-api)
5. [Subcontractor Manual Creation](#5-subcontractor-manual-creation)
6. [Hierarchy and Multi-Agency](#6-hierarchy-and-multi-agency)
7. [Subcontractor Contacts (Director, PM, Billing)](#7-subcontractor-contacts-director-pm-billing)
8. [Regulatory Documents and Status](#8-regulatory-documents-and-status)
9. [Subcontracts and Services](#9-subcontracts-and-services)
10. [Sites Linkage](#10-sites-linkage)
11. [Blocking Rules in Quotes and Purchase Orders](#11-blocking-rules-in-quotes-and-purchase-orders)
12. [Reports and KPIs](#12-reports-and-kpis)
13. [Acceptance Scenarios S1–S5](#13-acceptance-scenarios-s1–s5)
14. [Quick Mock Dataset (Copy/Paste)](#14-quick-mock-dataset-copypaste)
15. [Troubleshooting](#15-troubleshooting)

---

## 1) Where to Find Module 4 in the UI

Navigation:
- **BTP Prospecting → Quotes & Articles → Suppliers & Subcontractors → Subcontractors**
- **BTP Prospecting → Quotes & Articles → Suppliers & Subcontractors → Supplier Search**
- **BTP Prospecting → Quotes & Articles → Subcontracts**
- **BTP Prospecting → Quotes & Articles → Reports**
  - **Subcontractor Analysis**
  - **Subcontractor Reminders**

If not visible:
- Ensure your user has **BTP Salesperson**, **BTP Manager**, or **BTP Administrator** group.
- Logout and login again to refresh menus.

---

## 2) Prerequisites and Mock Users

Use the same demo users as Module 1–3:
- Alice Martin (Salesperson, BTP France)
- Bernard Leroy (Salesperson, BTP France)
- Emma Petit (Salesperson, BTP Belgium)
- David Roche (Manager, BTP France)

---

## 3) Configuration (Blocking + Expiration Alerts)

Navigation: **Settings → General Settings → BTP**

Settings:
- **Block subcontractors without valid documents**: ✅
- **Document expiration warning (days)**: `30`

These settings control:
- Automatic blocking of subcontractors in quotes and purchase orders.
- Expiration alerts and reminder emails.

---

## 4) Subcontractor Creation via API

Navigation: **Quotes & Articles → Suppliers & Subcontractors → Supplier Search**

Mock Data:
- **Type**: `Subcontractor`
- **SIREN**: `987654321`

Expected:
- If API returns data, a subcontractor is created automatically.
- If no data is returned, a manual creation form opens with pre-filled SIREN.

---

## 5) Subcontractor Manual Creation

Navigation: **Quotes & Articles → Suppliers & Subcontractors → Subcontractors → Create**

Mock Data:
- **Company Name**: `Atlas Subcontracting`
- **SIREN**: `987654321`
- **SIRET**: `98765432100011`
- **NAF Code**: `4322A`
- **Capital**: `150000`
- **Phone**: `+33 1 45 00 00 00`
- **Email**: `contact@atlas-subcontracting.fr`
- **Website**: `https://atlas-subcontracting.fr`
- **Is Subcontractor**: ✅

Save.

---

## 6) Hierarchy and Multi-Agency

This section is detailed because the Group/Subsidiary/Agency records must exist first.

### 6.1 Create the Group
Navigation: **BTP Prospecting → Clients & Contacts → Configuration → Company Hierarchy → Groups**

Create:
- **Group Name**: `Atlas Group`
- **Active**: ✅
Save.

If you want to use the **BTP France** hierarchy and it does not exist yet:
- Create a new group named `BTP France` here.

### 6.2 Create the Subsidiary
Navigation: **BTP Prospecting → Clients & Contacts → Configuration → Company Hierarchy → Subsidiaries**

Create:
- **Subsidiary Name**: `Atlas IDF`
- **Group**: `Atlas Group`
- **Active**: ✅
Save.

If you created **BTP France**:
- Create a subsidiary named `BTP France / Île‑de‑France`
- Set **Group** = `BTP France`

### 6.3 Create the Agency
Navigation: **BTP Prospecting → Clients & Contacts → Configuration → Company Hierarchy → Agencies**

Create:
- **Agency Name**: `Atlas Paris`
- **Group**: `Atlas Group`
- **Subsidiary**: `Atlas IDF`
- **Active**: ✅
Save.

If you created **BTP France**:
- Create agencies:
  - `BTP France / Paris` under `BTP France / Île‑de‑France`
  - `BTP France / Lyon` under a `BTP France / Auvergne‑Rhône‑Alpes` subsidiary (create it if needed)

### 6.4 Assign Hierarchy to the Subcontractor
Open **Atlas Subcontracting** (subcontractor form) and set:
- **Group**: `Atlas Group`
- **Subsidiary**: `Atlas IDF`
- **Agency**: `Atlas Paris`

### 6.5 Attach Multiple Agencies
In subcontractor form:
- **Attached Agencies**:
  - `BTP France / Paris`
  - `BTP France / Lyon`

Expected:
- Subcontractor can be linked to multiple agencies.
- When a subcontract is assigned to a site, the site agency must match one of the attached agencies.

---

## 7) Subcontractor Contacts (Director, PM, Billing)

In subcontractor form:
- **Director**: `Jean Dubois`
- **Project Manager**: `Sophie Martin`
- **Billing Administrator**: `Paul Leroy`

Tip: Create these as contacts under the subcontractor (child contacts).

---

## 8) Regulatory Documents and Status

Open subcontractor → **Regulatory Documents** tab → Add documents.

Mock Documents:
1) **URSSAF Certificate**
   - Reference: `URSSAF-2026-001`
   - Issue Date: `2026-01-01`
   - Expiration Date: `2026-12-31`

2) **Tax Certificate**
   - Reference: `TAX-2026-001`
   - Issue Date: `2026-01-01`
   - Expiration Date: `2026-12-31`

3) **Decennial Insurance**
   - Reference: `DEC-2026-001`
   - Issue Date: `2026-01-01`
   - Expiration Date: `2026-12-31`

4) **Civil Liability Insurance**
   - Reference: `RC-2026-001`
   - Issue Date: `2026-01-01`
   - Expiration Date: `2026-12-31`

5) **Paid Vacations Certificate**
   - Reference: `CONGE-2026-001`
   - Issue Date: `2026-01-01`
   - Expiration Date: `2026-12-31`

6) **Qualification Certificate**
   - Reference: `QUALIBAT-2026-001`
   - Issue Date: `2026-01-01`
   - Expiration Date: `2026-12-31`

Expected:
- Status shows `Valid` if not expired.
- Alerts appear when expiration is within the warning window.
- Automatic reminders are logged in **Reports → Subcontractor Reminders**.

---

## 9) Subcontracts and Services

Navigation: **Quotes & Articles → Subcontracts → Create**

Mock Data:
- **Subcontractor**: `Atlas Subcontracting`
- **Site**: `BTP France / Site A`
- **Start Date**: `2026-02-01`
- **End Date**: `2026-03-15`

Services tab:
1) Service: `Fireproof spraying`
   - Quantity: `250`
   - Unit: `m²`
   - Unit Price: `42.00`

2) Service: `Finishing works`
   - Quantity: `1`
   - Unit: `Lot`
   - Unit Price: `1500.00`

Expected:
- Executed Quantity and Invoiced Amount are computed.
- Documents tab shows linked regulatory documents.

---

## 10) Sites Linkage

Navigation: **Clients & Contacts → Sites**

Open the site:
- Subcontracts are listed in the **Subcontracts** tab.
- Site list shows **Subcontract Count**.

---

## 11) Blocking Rules in Quotes and Purchase Orders

### Subcontracting Labor (Quotes)
If a subcontractor is blocked (expired/missing docs):
- Adding them to a subcontracting labor line will raise a validation error.

### Purchase Orders
If a subcontractor is blocked:
- Purchase order confirmation is blocked (configurable in Settings).

---

## 12) Reports and KPIs

Navigation: **Reports → Subcontractor Analysis**

KPIs available:
- Conformity status
- Conformity rate
- Documents count
- Sites count
- Subcontracts count
- Total amount and total invoiced

Navigation: **Reports → Subcontractor Reminders**
- Full history of reminders sent to subcontractors

---

## 13) Acceptance Scenarios S1–S5

**S1 — Creation via API**
Input SIREN `987654321` → subcontractor auto-created.

**S2 — Expired Certificate**
Set URSSAF expiration to past date → subcontractor becomes blocked.

**S3 — Attached Contract**
Create subcontract → documents are checked on confirm.

**S4 — Multi-Agencies**
Attach subcontractor to multiple agencies → assign to site agency.

**S5 — Automatic Reminder**
Set document expiration within warning window → email reminder + reminder log.

---

## 14) Quick Mock Dataset (Copy/Paste)

Subcontractor:
- Name: Atlas Subcontracting
- SIREN: 987654321
- SIRET: 98765432100011
- NAF: 4322A
- Capital: 150000
- Phone: +33 1 45 00 00 00
- Email: contact@atlas-subcontracting.fr

Documents:
- URSSAF-2026-001
- TAX-2026-001
- DEC-2026-001
- RC-2026-001
- CONGE-2026-001
- QUALIBAT-2026-001

Services:
- Fireproof spraying / 250 m² / 42.00
- Finishing works / 1 Lot / 1500.00

---

## 15) Troubleshooting

- **Subcontractor blocked unexpectedly**: Check document expiration dates and status.
- **No reminders**: Ensure email is set and cron is running.
- **Cannot confirm subcontract**: Missing or expired documents.
- **Cannot assign subcontractor to site**: Agency mismatch.

---

If you want, I can also add a short **Module 4 troubleshooting checklist** in the admin menu similar to Module 3.

