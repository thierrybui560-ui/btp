## BTP Prospecting (Module 3) — Quotes & Articles

This guide provides step-by-step instructions with complete mock data for Module 3.
It follows the same structure and demo users as Module 1 and Module 2.

---

## Table of Contents

1. [Where to Find Module 3 in the UI](#1-where-to-find-module-3-in-the-ui)
2. [Prerequisites and Mock Users](#2-prerequisites-and-mock-users)
3. [Article Base Setup (Families, Subfamilies, Articles)](#3-article-base-setup-families-subfamilies-articles)
4. [Article Documents & Expiration Alerts](#4-article-documents--expiration-alerts)
5. [Price History & Fluctuation Report](#5-price-history--fluctuation-report)
6. [Suppliers & Subcontractors (Search + API)](#6-suppliers--subcontractors-search--api)
7. [Quote Structure (Lot → Title → Subtitle → Item)](#7-quote-structure-lot--title--subtitle--item)
8. [Items: Articles + Labor](#8-items-articles--labor)
9. [Quote Numbering & Revisions](#9-quote-numbering--revisions)
10. [Quote Sending & Follow-up](#10-quote-sending--follow-up)
11. [Reports & KPI](#11-reports--kpi)
12. [Acceptance Scenarios S1–S5](#12-acceptance-scenarios-s1–s5)
13. [Quick Mock Dataset (Copy/Paste)](#13-quick-mock-dataset-copypaste)
14. [Troubleshooting](#14-troubleshooting)

---

## 1) Where to Find Module 3 in the UI

Navigation:
- **BTP Prospecting → Quotes & Articles**
  - **Quotes**
  - **Articles**
    - Article Families
    - All Articles
  - **Suppliers & Subcontractors**
    - Suppliers
    - Subcontractors
    - Supplier Search
  - **Reports** (Manager only)
    - Quote Follow-up
    - Article Analysis
    - Supplier Analysis
    - Price Fluctuations

If not visible:
- Make sure your user has **BTP Salesperson**, **BTP Manager**, or **BTP Administrator** group.
- Logout and login again to refresh menus.

---

## 2) Prerequisites and Mock Users

Use the same demo users as Module 1 and 2:
- Alice Martin (Salesperson, BTP France)
- Bernard Leroy (Salesperson, BTP France)
- Emma Petit (Salesperson, BTP Belgium)
- David Roche (Manager, BTP France)

Optional hierarchy:
- Manager = David for Alice and Bernard.

---

## 3) Article Base Setup (Families, Subfamilies, Articles)

### 3.1 Create an Article Family
Navigation: **Quotes & Articles → Articles → Article Families → Create**

Mock Data:
- **Family Name**: `Flockings`
- **Sequence**: `10`
- **Active**: ✅
Save.

### 3.2 Create Subfamilies
Open `Flockings` → Subfamilies tab → Add lines:

Mock Data:
- `Fireproof`
- `Acoustic`

Save.

### 3.3 Create an Article
Navigation: **Quotes & Articles → Articles → All Articles → Create**

Mock Data:
- **Is BTP Article**: ✅
- **Name**: `Fireproof mortar`
- **Internal Reference**: `FLK-FR-001`
- **Designation**: `Fireproof mortar for concrete flocking`
- **Family**: `Flockings`
- **Subfamily**: `Fireproof`
- **Unit of Measure**: `kg`
- **Catalog Price**: `12.50`

Save.

Expected:
- Article is grouped under Family/Subfamily
- You can attach documents and price history

---

## 4) Article Documents & Expiration Alerts

Open the article → **Documents** tab → Add documents:

Mock Data:
- **Document Type**: `Test Report (PV)`
- **Document Name**: `PV Fireproof Mortar 2025`
- **Reference**: `PV-2025-001`
- **Issue Date**: `2025-01-10`
- **Expiration Date**: `2026-01-10`
- **Attachment**: upload any PDF

Expected:
- “Expires soon” and “Expired” indicators in the list
- Daily cron creates reminder activities when expiration is near

---

## 5) Price History & Fluctuation Report

Open article → **Price History** tab → Add lines:

Mock Data:
- **Supplier**: `Bouygues Matériaux`
- **Purchase Date**: `2025-02-01`
- **Purchase Price**: `8.90`
- **Quantity**: `100`

Repeat with different months to generate trends.

Report:
- **Quotes & Articles → Reports → Price Fluctuations**
Expected:
- Monthly average, min, max prices per article/supplier

---

## 6) Suppliers & Subcontractors (Search + API)

### 6.1 Supplier Search Wizard
Navigation: **Quotes & Articles → Suppliers & Subcontractors → Supplier Search**

Mock Data:
- **Type**: `Supplier`
- **SIREN**: `123456789`

Expected:
- If API returns data → Supplier created automatically
- If not found → error message

### 6.2 Manual Supplier Creation
If API fails, click **Create Manually**:

Mock Data:
- **Name**: `Bouygues Matériaux`
- **SIREN**: `123456789`
- **SIRET**: `12345678900019`
- **NAF Code**: `4673A`
- **Phone**: `+33 1 44 00 00 00`
- **Email**: `contact@bouygues-materiaux.fr`
- **Is Supplier**: ✅

Attach documents:
- URSSAF certificate
- Insurance
With expiration dates

Expected:
- Expiration alerts appear in supplier form

---

## 7) Quote Structure (Lot → Title → Subtitle → Item)

Navigation: **Quotes & Articles → Quotes → Create**

Mock Data:
- **Customer**: `Vinci Energies`
- **Quotation Date**: today

Add **Lots**:
Lot 1:
- **Name**: `Fireproof flocking`

Inside Lot 1, add **Title**:
- **Name**: `Wall flocking`

Inside Title, add **Subtitle**:
- **Name**: `Concrete flocking`

Inside Subtitle, add **Item**:
- **Name**: `Application flocking thickness 3 cm`
- **Quantity**: `250`
- **Unit**: `m²`
- **Unit Price**: `38.00`

Expected:
- Items roll up in totals
- The quote is structured and readable

---

## 8) Items: Articles + Labor

Open the Item → **Articles** tab:
- **Article**: `Fireproof mortar`
- **Quantity**: `500`

Open the Item → **Labor** tab:

### Internal Yield (Method 1)
- **Labor Type**: `Internal Yield`
- **Hourly Cost**: `45`
- **Yield per hour**: `20`
- **Quantity**: `250`

### Subcontracting (Method 2)
- **Labor Type**: `Subcontracting`
- **Subcontractor**: `ABC Flocage`
- **Unit Price**: `12`
- **Quantity**: `250`

Expected:
- Total costs are computed and margins are visible

---

## 9) Quote Numbering & Revisions

Save the quote:
Expected number format: `YYYYMMNNN`
Example: `202501001`

If the quote is sent and later edited:
- Use **Create Revision**
Expected: `202501001A`, `202501001B`, ...

---

## 10) Quote Sending & Follow-up

Click **Send Quote**:
- Uses standard Odoo email flow
- Sets quote to **Sent**
- Schedules follow-up date (default 7 days)

Follow-up reminders:
- Daily cron checks `Next Follow-up Date`
- Creates activity for the salesperson

---

## 11) Reports & KPI

### Quote Follow-up
Navigation: **Quotes & Articles → Reports → Quote Follow-up**

Expected:
- Quotes grouped by salesperson and status
- Average delay between creation and sending (Days to Send)

### Article Analysis
Navigation: **Reports → Article Analysis**

Expected:
- Most used articles
- Quantities and total costs

### Supplier Analysis
Navigation: **Reports → Supplier Analysis**

Expected:
- Purchase price comparison by supplier

### Price Fluctuations
Navigation: **Reports → Price Fluctuations**

Expected:
- Monthly average price trends

---

## 12) Acceptance Scenarios S1–S5

### S1 — Article creation
Create `Fireproof mortar` in `Flockings → Fireproof` and attach TS + PV with validity dates.

Expected:
- Document is listed with expiration info

### S2 — Quote modified after sending
Send quote `202501001` then click **Create Revision**.

Expected:
- New quote `202501001A` opens in draft

### S3 — Supplier creation via API
Search SIREN `123456789` in Supplier Search wizard.

Expected:
- Supplier created with pre-filled legal data

### S4 — Document expiration alert
Supplier URSSAF expires tomorrow.

Expected:
- Activity created for salesperson

### S5 — Price history follow-up
Add price history entries over 3 months.

Expected:
- Price Fluctuations report shows average line trend

---

## 13) Quick Mock Dataset (Copy/Paste)

### Article Families
- `Flockings`
  - `Fireproof`
  - `Acoustic`

### Articles
- **Fireproof mortar**
  - Internal Ref: `FLK-FR-001`
  - UoM: `kg`
  - Catalog Price: `12.50`

### Suppliers
- **Bouygues Matériaux**
  - SIREN: `123456789`
  - SIRET: `12345678900019`
  - NAF: `4673A`

### Subcontractor
- **ABC Flocage**
  - SIREN: `987654321`

### Quote Example
- Lot: `Fireproof flocking`
  - Title: `Wall flocking`
    - Subtitle: `Concrete flocking`
      - Item: `Application flocking thickness 3 cm`
        - Qty: `250 m²`
        - Unit Price: `38.00`

---

## 14) Troubleshooting

**Issue: Quote numbers not generated**
- Ensure the `btp.quote` sequence exists.
- Upgrade `btp_prospecting` after installing.

**Issue: Follow-up reminders not sent**
- Check cron: **Settings → Technical → Automation → Scheduled Actions**
- Ensure `BTP Quote: Follow-up Reminders` is active.

**Issue: API not enriching suppliers**
- Check API keys in **Settings → Technical → Parameters → System Parameters**
  - `btp_prospecting.pappers_api_key`
  - `btp_prospecting.insee_api_key`
  - `btp_prospecting.infogreffe_api_key`

**Issue: Price Fluctuations empty**
- Ensure price history lines exist for articles.


