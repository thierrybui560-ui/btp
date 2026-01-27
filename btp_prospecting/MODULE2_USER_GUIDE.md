## BTP Prospecting (Module 2) — Clients & Contacts Management

This guide provides step-by-step instructions with complete mock data for Module 2.
It is aligned with the Module 2 requirements and uses the same demo users as Module 1.

---

## Table of Contents

1. [Where to Find Module 2 in the UI](#1-where-to-find-module-2-in-the-ui)
2. [Prerequisites and Mock Users](#2-prerequisites-and-mock-users)
3. [Company Hierarchy Setup (Group → Subsidiary → Agency)](#3-company-hierarchy-setup-group--subsidiary--agency)
4. [Company Creation + API Enrichment (SIREN)](#4-company-creation--api-enrichment-siren)
5. [Contact Creation + Duplicate Control](#5-contact-creation--duplicate-control)
6. [Contact Career Change Scenario](#6-contact-career-change-scenario)
7. [Shared Client Scenario (Multi-Company)](#7-shared-client-scenario-multi-company)
8. [Pyramidal Visibility & Assignment](#8-pyramidal-visibility--assignment)
9. [Search & Anti-Duplicate Quick Tests](#9-search--anti-duplicate-quick-tests)
10. [Acceptance Scenarios S1–S5](#10-acceptance-scenarios-s1–s5)
11. [Quick Mock Dataset (Copy/Paste)](#11-quick-mock-dataset-copypaste)
12. [Troubleshooting](#12-troubleshooting)

---

## 1) Where to Find Module 2 in the UI

Navigation:
- **BTP Prospecting → Clients & Contacts**
  - **Companies**
  - **Contacts**
  - **Company Hierarchy**
    - Groups
    - Subsidiaries
    - Agencies

If not visible:
- Make sure your user has **BTP Salesperson**, **BTP Manager**, or **BTP Administrator** group.
- Logout and login again to refresh menus.

---

## 2) Prerequisites and Mock Users

Use the same users from Module 1:
- Alice Martin (Salesperson, BTP France)
- Bernard Leroy (Salesperson, BTP France)
- Emma Petit (Salesperson, BTP Belgium)
- David Roche (Manager, BTP France)

Optional hierarchy:
- Manager = David for Alice and Bernard.

---

## 3) Company Hierarchy Setup (Group → Subsidiary → Agency)

### 3.1 Create Group
Navigation: **BTP Prospecting → Clients & Contacts → Company Hierarchy → Groups → Create**

Mock Data:
- **Group Name**: `Bouygues Construction`
- **SIREN**: `552123456`
- **Active**: ✅
Save.

### 3.2 Create Subsidiary
Navigation: **Company Hierarchy → Subsidiaries → Create**

Mock Data:
- **Subsidiary Name**: `Bouygues Bâtiment Île-de-France`
- **Group**: `Bouygues Construction`
- **SIREN**: `552123457`
- **Active**: ✅
Save.

### 3.3 Create Agency
Navigation: **Company Hierarchy → Agencies → Create**

Mock Data:
- **Agency Name**: `Bouygues Bâtiment – West Agency`
- **Subsidiary**: `Bouygues Bâtiment Île-de-France`
- **SIRET**: `55212345700019`
- **Active**: ✅
Save.

Expected:
- You can open Group → see Subsidiaries
- Open Subsidiary → see Agencies
- Open Agency → see Companies tab

---

## 4) Company Creation + API Enrichment (SIREN)

### 4.1 Create Company (Salesperson)
User: **Alice**

Navigation: **BTP Prospecting → Clients & Contacts → Companies → Create**

Mock Data:
- **Company Name**: `Vinci Energies`
- **SIREN**: `552091234`
- **SIRET**: `55209123400022`
- **NAF Code**: `4321A`
- **Legal Form**: `SAS`
- **Capital**: `5000000`
- **Group**: `Bouygues Construction` (for testing hierarchy)
- **Subsidiary**: `Bouygues Bâtiment Île-de-France`
- **Agency**: `Bouygues Bâtiment – West Agency`
- **Assigned Salesperson**: `Alice Martin`
- **Is Prospect**: ✅
- **Is Client**: (readonly, false until orders)

Save.

### 4.2 Enrich from API
On the company form, click **"Enrich from API"**.

Expected:
- Fields may fill (name, address, NAF code, etc.)
- `API Enriched` becomes ✅
- `Data Source` = `Pappers` or `INSEE`

---

## 5) Contact Creation + Duplicate Control

### 5.1 Create Contact (Unique)
User: **Alice**

Navigation: **Contacts → Create**

Mock Data:
- **Name**: `Jean Dupont`
- **Job Title**: `Project Manager`
- **Email**: `jean.dupont@vinci-energies.fr`
- **Phone**: `+33 1 80 20 30 40`
- **Company**: `Vinci Energies`
- **Assigned Salesperson**: `Alice Martin`

Save.

Expected:
- Contact created
- Career history auto-updated (current company)

### 5.2 Attempt Duplicate Contact
Create another contact with:
- **Name**: `Jean Dupont`
- **Email**: `jean.dupont@vinci-energies.fr`
- **Phone**: `+33 1 80 20 30 40`

Expected:
- Warning or error: duplicate exists and is assigned to a salesperson
- If you must proceed, enable **"Force Duplicate"** and save
- Manager receives a notification if forced with identical email/phone

---

## 6) Contact Career Change Scenario

### 6.1 Move a Contact to New Company
User: **Alice**

Steps:
1. Open contact **Jean Dupont**
2. Change **Company** from `Vinci Energies` to `Eiffage Construction`
3. Update **Job Title** to `Senior Buyer`
4. Save

Expected:
- Previous career entry end_date filled
- New career entry created with new company and job title
- Current company updated to `Eiffage Construction`

---

## 7) Shared Client Scenario (Multi-Company)

### 7.1 Create a Shared Company
User: **David (Manager)**

Create company:
- **Company Name**: `Bouygues Immobilier`
- **SIREN**: `352987654`
- **Assigned Salesperson**: `Bernard Leroy`
- **Shared Companies**: `BTP France`, `BTP Belgium`

Expected:
- Users from both companies can access the same client record
- Legal data (SIREN, address) is common

---

## 8) Pyramidal Visibility & Assignment

### 8.1 Salesperson Visibility
User: **Alice**

Expected:
- Sees only companies where **Assigned Salesperson = Alice**
- Sees only contacts where **Assigned Salesperson = Alice**

### 8.2 Manager Visibility
User: **David**

Expected:
- Sees all companies and contacts
- Can reassign companies or contacts

---

## 9) Search & Anti-Duplicate Quick Tests

### 9.1 Company Search (Salesperson)
Navigation: **BTP Prospecting → Clients & Contacts → Company Search**

Search by name or SIREN/SIRET:
```
Bouygues
```
or
```
552091234
```
Expected:
- Returns a short list of matching companies (no full browsing)
- Shows SIREN/SIRET and assigned salesperson

### 9.2 Search by SIREN (Companies list)
Search in Companies list:
```
552091234
```
Expected: Company appears.

### 9.3 Duplicate Company Check
Try creating a company with same SIREN/SIRET.
Expected: Blocked with “Company already exists” message.

### 9.4 Contact Duplicate Flow (Force or Cancel)
Create a contact with same name + email/phone/mobile.
Expected:
- Duplicate warning displayed
- User can cancel and open the existing contact manually
- **Force Duplicate** remains available if needed (triggers manager activity if exact match)

---

## 10) Acceptance Scenarios S1–S5

### S1 — Company creation with API enrichment
Salesperson enters SIREN → API fills data → company created.
Test: Section 4.

### S2 — Contact duplicate
Create duplicate contact with same email/phone/mobile.
Expected:
- Warning about assigned salesperson
- User can cancel and open the existing record manually
- Force duplicate triggers manager notification if exact match

### S3 — Company change (career update)
Change contact company; history preserved.
Test: Section 6.

### S4 — Shared client
Company shared between BTP France and BTP Belgium.
Test: Section 7.

### S5 — Reattribution
Manager reassigns multiple companies/contacts to another salesperson.
Expected: Assignment updated; history preserved (contacts keep career history).

---

## 11) Multi-Address, Sites, and Commercial Conditions

### 11.1 Multiple Addresses
Open a company → **Addresses** tab.
Expected:
- Add Headquarters / Agency / Site / Other addresses
- Each address supports full contact details

### 11.2 Sites Linked to Agencies
Navigation: **BTP Prospecting → Clients & Contacts → Sites**
Expected:
- Create sites linked to an **Agency**
- Link site to a company and contacts

### 11.3 Commercial Conditions (Per Company)
Open a company → **Commercial Conditions** tab.
Expected:
- One line per operating company
- Set pricelist, payment term, incoterm

---

## 12) Reports & KPIs

Navigation: **BTP Prospecting → Clients & Contacts → Reports**
Expected:
- **Company KPIs**: prospects vs clients, contact coverage
- **Contact KPIs**: contact list by salesperson
- **Contact Career History**: full history per contact

---

## 13) Quick Mock Dataset (Copy/Paste)

### Companies
1. **Vinci Energies**
   - SIREN: `552091234`
   - SIRET: `55209123400022`
   - NAF: `4321A`
   - Legal Form: `SAS`
   - Capital: `5000000`
   - Assigned: `Alice Martin`

2. **Eiffage Construction**
   - SIREN: `775331122`
   - SIRET: `77533112200011`
   - NAF: `4211Z`
   - Legal Form: `SA`
   - Capital: `15000000`
   - Assigned: `Bernard Leroy`

3. **Bouygues Immobilier**
   - SIREN: `352987654`
   - SIRET: `35298765400033`
   - NAF: `4110A`
   - Legal Form: `SAS`
   - Capital: `8000000`
   - Assigned: `Bernard Leroy`
   - Shared Companies: `BTP France`, `BTP Belgium`

### Contacts
1. **Jean Dupont**
   - Email: `jean.dupont@vinci-energies.fr`
   - Phone: `+33 1 80 20 30 40`
   - Mobile: `+33 6 10 20 30 40`
   - Company: `Vinci Energies`
   - Job Title: `Project Manager`
   - Assigned: `Alice Martin`

2. **Claire Martin**
   - Email: `claire.martin@eiffage.fr`
   - Phone: `+33 1 70 10 20 30`
   - Mobile: `+33 6 20 30 40 50`
   - Company: `Eiffage Construction`
   - Job Title: `Buyer`
   - Assigned: `Bernard Leroy`

3. **Lucas Bernard**
   - Email: `lucas.bernard@bouygues-immobilier.fr`
   - Phone: `+32 2 555 44 33`
   - Company: `Bouygues Immobilier`
   - Job Title: `Site Manager`
   - Assigned: `Emma Petit`

---

## 12) Troubleshooting

**Cannot create company with SIREN**
- Another company with same SIREN/SIRET exists.
- Search by SIREN and reuse existing record.

**Contact duplicate warning**
- If email/phone is the same: change values or force duplicate with manager approval.

**Visibility issues**
- Check assigned salesperson and manager hierarchy.
- Check that user belongs to correct group (BTP Salesperson / Manager / Admin).


