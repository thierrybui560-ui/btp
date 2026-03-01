# Module 13 — Multi-companies — User & Testing Guide

This guide helps you **use and test Module 13**: several group companies on the same Odoo with strict data separation, optional shared data (clients, articles, suppliers, commercial leads), and consolidated management views. It is based on the current BTP Prospecting implementation (Odoo 19).

---

## 1. What Module 13 Does (Summary)


| Goal                        | What the system does                                                                                                                                                                                                                                                                |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Company choice at login** | User selects the company to work in; only companies to which they have rights appear. Standard Odoo company switcher allows switching without logging out.                                                                                                                          |
| **Document per company**    | Each document (quote, invoice, site) is attached to a single company (`company_id`).                                                                                                                                                                                                |
| **Exclusive data**          | Accounting, invoices, payments, sites, HR remain per company and are restricted by company rules.                                                                                                                                                                                   |
| **Shared data**             | Clients can be shared (one legal file, commercial conditions per company via BTP Commercial Conditions). Suppliers and articles can be shared; articles use a common catalog with prices/suppliers per company. Leads can be shared (same lead, independent follow-up per company). |
| **Consolidation**           | Management has consolidated reports: turnover by company, cash/invoiced by company, net margin by company and site, and shared clients distribution.                                                                                                                                |


---

## 2. Feature List (What You Can Test)


| #   | Feature                                                                                 | Where to test                                                                                        | Section |
| --- | --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------- |
| F1  | **Company sharing settings** — SIREN, Use shared clients/suppliers/articles per company | BTP Prospecting → Multi-companies → Company Sharing Settings; or Settings → Companies → open company | 5.1     |
| F2  | **Shared client** — Same legal file (partner), commercial conditions per company        | Clients & Contacts → Companies → edit partner → Shared Companies + Commercial Conditions per company | 5.2     |
| F3  | **Shared lead** — Lead visible to several companies, each with its follow-up            | Leads → create/edit lead → Sharing type = Shared, Shared Companies = FR, BE                          | 5.3     |
| F4  | **Quote/Site “Shared client” flag** — Indicates document relates to a shared client     | Quotes list (column “Shared client” optional); Site list (column “Shared client” optional)           | 5.4     |
| F5  | **Consolidated turnover** — CA by company + total                                       | Multi-companies → Consolidation Reports → New → Scope = Consolidated Turnover by Company             | 5.5     |
| F6  | **Consolidated cash / invoiced** — Invoiced amounts by company + total                  | Consolidation Reports → Scope = Consolidated Cash / Invoiced by Company                              | 5.6     |
| F7  | **Consolidated margin** — Net margin by company and site + total                        | Consolidation Reports → Scope = Consolidated Net Margin by Company & Site                            | 5.7     |
| F8  | **Shared clients distribution** — List of shared clients and which companies use them   | Consolidation Reports → Scope = Shared Clients Distribution                                          | 5.8     |


---

## 3. Where to Find Everything (UI Navigation)

### 3.1 BTP menu: Multi-companies


| Menu path                                                        | What you see                                                                                                                                 | Access               |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| **BTP Prospecting → Multi-companies → Company Sharing Settings** | List of companies (res.company). Open a company to set BTP SIREN and shared clients/suppliers/articles.                                      | BTP Manager / Admin. |
| **BTP Prospecting → Multi-companies → Consolidation Reports**    | Report templates filtered to consolidation scopes (turnover, cash, margin, shared clients). Create template, set period/company, run report. | BTP Manager / Admin. |


### 3.2 Company and document visibility


| Where                | What                                                                                                                                                                                  |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Company switcher** | Top-right: switch current company without logging out. Only companies allowed for the user are shown.                                                                                 |
| **Quotes / Sites**   | Each record has a company; list views can show optional column “Shared client” when the client is shared.                                                                             |
| **Leads**            | Lead has Company and Sharing type (exclusive / shared / global). Shared leads list “Shared companies”. Record rules restrict visibility to the user’s companies and shared companies. |


### 3.3 Reports & KPIs (Module 13)


| Report scope                                  | Content                                                                                |
| --------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Consolidated Turnover by Company**          | Turnover (HT) per company from converted sale orders; last row = Total (consolidated). |
| **Consolidated Cash / Invoiced by Company**   | Invoiced total (HT) per company from posted customer invoices; last row = Total.       |
| **Consolidated Net Margin by Company & Site** | Rows: company, site, net margin, margin %; subtotal per company; last row = Total.     |
| **Shared Clients Distribution**               | Client name and list of companies with which the client is shared.                     |


On each report template you can set **Company** to restrict to one entity, or leave empty for full group consolidation.

---

## 4. Connection & Company Selection

- **At login**: The user chooses the company (or gets the default) among companies they are allowed to use (`allowed_company_ids`).
- **Without logging out**: Use the company drop-down in the top bar to switch company.
- **Documents**: Every quote, invoice, and site is attached to one company (`company_id`). The system limits visibility of companies and records according to assigned rights and record rules (e.g. leads: own company or shared companies).

---

## 5. Step-by-Step Tests

### 5.1 Company sharing settings (F1)

**Steps**

1. **BTP Prospecting → Multi-companies → Company Sharing Settings** (or **Settings → Companies** and open a company).
2. Open a company (e.g. French entity).
3. In **BTP Multi-company**: set **SIREN** (e.g. 123456789), check **Use Shared Clients**, **Use Shared Suppliers**, **Use Shared Articles** as needed.
4. Save.

**Expected**

- Company form shows the BTP Multi-company group. Values are saved and used for policy (shared clients/suppliers/articles). Other modules (e.g. partner visibility, commercial conditions) rely on these flags and on partner/lead sharing fields.

### 5.2 Shared client and commercial conditions (F2)

**Steps**

1. **Clients & Contacts → Companies** → create or open a client (company type).
2. In **BTP** (or equivalent) set **Shared Companies** to e.g. FR and BE (companies that share this client).
3. Open **Commercial Conditions** (or **BTP Company Commercial Conditions**): add one line per operating company (e.g. FR: pricelist X, payment term 30 days; BE: pricelist Y, payment term 45 days).
4. Save.

**Expected**

- One legal file (partner) for the client; commercial conditions are specific per company. Both FR and BE users (with rights) can see and use this client according to record rules.

### 5.3 Shared lead (F3)

**Steps**

1. **Leads →** create or edit a lead.
2. Set **Company** to e.g. FR (main company).
3. Set **Sharing type** to **Shared**.
4. Set **Shared companies** to FR and BE.
5. Save.

**Expected**

- Lead is visible to users whose current company is FR or BE (and who have lead access). Each company can have its own follow-up (assignee, stages, etc.) while the lead record is shared.

### 5.4 Quote and site “Shared client” (F4)

**Steps**

1. Create a **Quote** with **Client** = a partner that has **Shared Companies** set (e.g. Bouygues Construction shared with FR and BE).
2. Save; optionally show the “Shared client” column in the Quotes list.
3. Convert to order so a **Site** is created; open the site.
4. In the Sites list, optionally show the “Shared client” column.

**Expected**

- Quote and site show **Shared client** = true (computed from the client’s shared companies). Column is optional in list views.

### 5.5 Consolidated turnover report (F5)

**Steps**

1. **BTP Prospecting → Multi-companies → Consolidation Reports** → **New**.
2. **Report Name** = e.g. “Group CA”.
3. **Scope** = **Consolidated Turnover by Company**.
4. **From Date** / **To Date** = desired period (or leave empty for all).
5. **Company** = leave empty for full group, or select one company to restrict.
6. **Output Format** = PDF or Excel.
7. Save, then **Generate (no email)** or **Generate and Send by Email**.

**Expected**

- Report lists one row per company with turnover (HT), then a row **Total (consolidated)**. File is generated and can be downloaded from Export History.

### 5.6 Consolidated cash / invoiced report (F6)

**Steps**

1. In **Consolidation Reports**, create a new template.
2. **Scope** = **Consolidated Cash / Invoiced by Company**.
3. Set period and company filter as needed; run the report.

**Expected**

- Rows: company name, invoiced total (HT) from posted customer invoices; last row = Total (consolidated).

### 5.7 Consolidated margin report (F7)

**Steps**

1. New template, **Scope** = **Consolidated Net Margin by Company & Site**.
2. Optionally set **Company** to one entity.
3. Run the report.

**Expected**

- Rows: Company, Site, Net Margin, Margin %; subtotal row per company; last row = Total (consolidated).

### 5.8 Shared clients distribution (F8)

**Steps**

1. New template, **Scope** = **Shared Clients Distribution**.
2. Run the report (no period filter; uses all shared clients).

**Expected**

- List of clients (companies) that have **Shared Companies** set, with the list of company names they are shared with.

---

## 6. Acceptance Scenarios (Spec Module 13)

### S1 — Restricted access: user only in company FR

1. Assign the user only to company **FR** (no BE in allowed companies).
2. Log in and switch company: only FR appears.
3. **Verify**: User does not see company BE; leads, partners, and documents of BE are not accessible (enforced by company and record rules).

### S2 — Shared client: Bouygues Construction = shared FR and BE

1. Create or select client **Bouygues Construction**; set **Shared Companies** = FR and BE.
2. Add **Commercial Conditions**: one line for FR (e.g. pricelist, payment term), one for BE (different conditions).
3. **Verify**: One legal file (SIREN, address); commercial conditions are distinct per company. Users of FR and BE (with rights) see the client and use the correct conditions for their company.

### S3 — Common article: “Fireproof mortar” shared, price FR 10€/kg, BE 12€/kg

1. Use a **shared article** (product with `company_id` = False or shared) and set **pricelists** or **supplier info** per company (FR: 10€/kg, BE: 12€/kg) via Odoo pricelists / product form.
2. **Verify**: Same article in catalog; selling/purchase prices or conditions can differ by company (Odoo standard + BTP commercial conditions / pricelists per company).

### S4 — Multi-company lead: international site, separate FR and BE follow-up

1. Create a lead; **Sharing type** = **Shared**, **Shared companies** = FR and BE.
2. Assign or process the lead from company FR (e.g. assignee FR); switch to BE and ensure BE users can see the same lead and add their follow-up (e.g. different assignee or notes).
3. **Verify**: Same lead record; both companies see it; follow-up can be independent (assignee, activities) per company usage.

### S5 — Consolidation: management consults consolidated group CA, then detail by entity

1. **Multi-companies → Consolidation Reports** → create template **Consolidated Turnover by Company**, **Company** = empty.
2. Run the report.
3. **Verify**: Report shows CA per company and **Total (consolidated)**. Then create the same scope with **Company** = FR only; run again and verify only FR row(s) and total for FR.

---

## 7. Troubleshooting


| Problem                                         | What to check                                                                                                                                                                                   |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **User does not see a company**                 | User’s **Allowed companies** (Settings → Users → Companies). User must have at least one company.                                                                                               |
| **User sees leads/partners of another company** | Record rules: leads use company_id and shared_company_ids; partners use btp_assigned_salesperson_id and btp_shared_company_ids. Ensure rules are applied and multi-company is enabled.          |
| **Shared client not visible in other company**  | Partner **Shared Companies** must include that company. User must have that company in allowed companies and have BTP partner/lead rights.                                                      |
| **Consolidation report empty**                  | Check **From/To** dates and **Company** filter. For turnover: need converted sale orders (state sale/done). For cash: need posted customer invoices. For margin: need sites with btp_site_code. |
| **BTP Multi-company group not on company form** | Module 13 views must be loaded; upgrade the module. Inherited view is `res.company.form.btp.multi.company`.                                                                                     |
| **“Shared client” always false on quote/site**  | Quote: partner must have **Shared Companies** set. Site: computed from source quote’s partner; ensure quote has the shared client.                                                              |


---

## 8. Quick Reference — Key Fields

### res.company (extended for Module 13)


| Field                | Meaning                                             |
| -------------------- | --------------------------------------------------- |
| btp_siren            | Optional 9-digit SIREN for this company.            |
| btp_shared_clients   | Use shared clients (policy flag).                   |
| btp_shared_suppliers | Use shared suppliers (policy flag).                 |
| btp_shared_articles  | Use shared articles / common catalog (policy flag). |


### res.partner (existing, used by Module 13)


| Field                  | Meaning                                       |
| ---------------------- | --------------------------------------------- |
| btp_shared_company_ids | Companies that share this client (many2many). |


### btp.lead (existing)


| Field              | Meaning                                             |
| ------------------ | --------------------------------------------------- |
| company_id         | Main company of the lead.                           |
| sharing_type       | exclusive / shared / global.                        |
| shared_company_ids | Companies that can see/use this lead (when shared). |


### btp.company.commercial.condition (existing)


| Field                                      | Meaning                                         |
| ------------------------------------------ | ----------------------------------------------- |
| partner_id                                 | Client (company).                               |
| company_id                                 | Operating company (conditions are per company). |
| pricelist_id, payment_term_id, incoterm_id | Commercial conditions for this company.         |


### sale.order (extended)


| Field         | Meaning                                                        |
| ------------- | -------------------------------------------------------------- |
| company_id    | Company of the quote (Odoo standard).                          |
| btp_is_shared | True when the client (partner) is shared with other companies. |


### project.project / BTP Site (extended)


| Field         | Meaning                                        |
| ------------- | ---------------------------------------------- |
| company_id    | Company of the site (Odoo standard).           |
| btp_is_shared | True when the source quote’s client is shared. |


### Report template scopes (Module 13)


| Scope                       | Description                                                     |
| --------------------------- | --------------------------------------------------------------- |
| consolidated_turnover       | Turnover (HT) by company + total from sale orders (sale/done).  |
| consolidated_cash           | Invoiced total (HT) by company + total from posted out_invoice. |
| consolidated_margin         | Net margin by company and site + subtotals + total.             |
| shared_clients_distribution | Client name and list of shared companies.                       |


---

## 9. Summary Checklist

- **Company selection**: Users choose company at login and can switch via the company drop-down; only allowed companies are visible.
- **Documents** (quotes, invoices, sites) are attached to one company; optional **Shared client** flag on quote/site when the client is shared.
- **Shared clients**: One legal file (partner), **Shared Companies** + **Commercial Conditions** per company (btp.company.commercial.condition).
- **Shared leads**: **Sharing type** = Shared, **Shared companies** = list; visibility and follow-up can be per company.
- **Articles**: Common catalog; prices and conditions per company (Odoo pricelists / supplierinfo + BTP conditions).
- **Consolidation**: Use **Multi-companies → Consolidation Reports** to run turnover, cash/invoiced, margin by company/site, and shared clients distribution. Set **Company** on the template to filter to one entity or leave empty for the full group.
- **Company settings**: **Multi-companies → Company Sharing Settings** (or Settings → Companies) to set per-company BTP SIREN and “Use shared clients/suppliers/articles”.

