# Module 11 - Reports & Exports

## Detailed Functional Guide + Full UAT Playbook (Odoo 19)

This guide is a client-delivery UAT document for Module 11.
It is written for key users, management, controllers, and testers.

---

## 1) Objective and Scope

Module 11 provides:

- Reusable report templates by business domain (commercial, sites, logistics, QHSE, supplier, governance).
- Single-click export to PDF, Excel, CSV.
- Scheduled generation and automatic email dispatch.
- Export traceability with execution status and downloadable files.
- Combined analytical scopes (cross dimensions: geography, site + supplier, salesperson + client).

---

## 2) Requirement-to-Implementation Matrix

| Requirement | Status | Current implementation |
| --- | --- | --- |
| Complete reporting framework by domain | Implemented | `btp.report.template` with multi-scope data providers |
| Standard reports (site/client/salesperson/article/supplier/QHSE) | Implemented | Dedicated scope methods in report template model |
| Additional reports (lot/employee/team/rotation) | Implemented | Added lot cost report, employee productivity, team performance, article rotation |
| Combined analytical reports | Implemented | Added geo-commercial, article+site+supplier, margin by salesperson+client |
| PDF / Excel / CSV export | Implemented | QWeb PDF + xlsxwriter + CSV renderer |
| Scheduled sending (daily/weekly/monthly) | Implemented | Cron: `BTP Reports: Scheduled Report Generation` |
| Period/company/geographic filters | Implemented | `date_from`, `date_to`, `company_id`, `geographic_area` |
| Email recipients configuration | Implemented | `recipient_user_ids` on template, restricted by company |
| Export history and status | Implemented | `btp.export.job` + list/form + template tab |
| Data storage inside Odoo | Implemented | Generated files stored as `ir.attachment` linked to export jobs |

---

## 3) Menus and Navigation

Main paths:

- `BTP Prospecting -> Reports & Exports -> Report Templates`
- `BTP Prospecting -> Reports & Exports -> Export History`
- `Settings -> Technical -> Automation -> Scheduled Actions` (admin)

Template form actions:

- **Generate and Send by Email**
- **Generate (no email)**
- **Exports** stat button (template-specific run history)

---

## 4) Data Model and Key Fields

## 4.1 Report Template (`btp.report.template`)

- `name`: report title
- `scope`: report dataset type
- `date_from`, `date_to`: period filter
- `company_id`: company filter
- `geographic_area`: city/zip/country text filter for geo scopes
- `output_format`: `pdf`, `xlsx`, `csv`
- `schedule`: `none`, `daily`, `weekly`, `monthly`
- `recipient_user_ids`: email recipients
- `export_job_ids`: generated run history

## 4.2 Export Job (`btp.export.job`)

- `report_template_id`
- `run_date`
- `state`: `pending`, `done`, `failed`
- `attachment_id`: generated file
- `error_message`

---

## 5) Available Report Scopes (What each scope returns)

## 5.1 Standard scopes

- **Leads & Quotes by Salesperson**
- **Site Progress, Costs & Margins** (includes QHSE incident count by site)
- **Business Volume by Client** (quotes/orders/conversion)
- **Salesperson Activity**
- **Article Consumption (planned vs actual)**
- **Supplier / Price Analysis** (avg price + conformity)
- **QHSE Incidents by Site**
- **Net Margin & Article Consumption**

## 5.2 Additional scopes

- **Costs & Consumption by Quote Lot**
- **Employee Productivity (hours, pointing, sites)**
- **Team Performance (yield, assigned sites)**
- **Article Rotation & Stock Movements**

## 5.3 Combined analytical scopes

- **Commercial Performance by Geographic Area**
- **Article Consumption by Site & Supplier**
- **Net Margin by Salesperson & Client**

---

## 6) Prerequisites for UAT

Use this minimum data pack:

1. Companies: at least one operating company.
2. Users:
   - `manager_user` with valid email.
   - `sales_user` with valid email.
3. Sites:
   - `Tour La Defense - Flocking`
   - `Demo Building Corp - 202602003`
4. Quotes/orders with salespersons and clients.
5. At least 2 incidents with different type/severity/site.
6. Article consumptions (`btp.site.consumption`) for at least 2 products.
7. Supplier price history (`btp.article.price.history`) with multiple dates.
8. Pointing entries for at least 2 users.
9. Optional: yield entries (`btp.site.performance`) for team report.

---

## 7) Detailed Acceptance Scenarios (S1-S5)

## S1 - Commercial report weekly generation + Excel email

**Goal**  
Validate weekly generation and email distribution of "Leads & Quotes by Salesperson".

**Preconditions**

- SMTP outgoing mail server configured.
- Recipient users have valid email.

**Steps**

1. Open `Reports & Exports -> Report Templates` and click **New**.
2. Set:
   - Name = `Weekly Commercial Activity`
   - Scope = `Leads & Quotes by Salesperson`
   - Output Format = `Excel`
   - Schedule = `Weekly`
   - Recipients = management users
3. Save.
4. Click **Generate and Send by Email**.
5. Open generated export job from the redirected form.
6. Download the file.

**Expected**

- Export job state = **Done**.
- Excel file contains salesperson rows and columns (quotes, converted, totals, leads converted).
- Email is sent to configured recipients with attachment.

**Evidence**

- Screenshot of template config.
- Screenshot/export job `Done`.
- Downloaded `.xlsx` file.

**Pass/Fail**

- Pass only if run completes and email + attachment are both delivered.

---

## S2 - Site report PDF export

**Goal**  
Validate PDF generation for site-level operational report.

**Steps**

1. Create template:
   - Scope = `Site Progress, Costs & Margins`
   - Output Format = `PDF`
   - Schedule = `Manual only`
2. Set optional period/company filter.
3. Click **Generate (no email)**.
4. Open export job and click **Download**.

**Expected**

- PDF is generated and downloadable.
- Data includes site code/name, quote total, invoiced, costs, net margin, margin %, incident count.

**Evidence**

- Export job screenshot (`Done`).
- First page of downloaded PDF.

---

## S3 - Supplier analysis over 12 months (Excel)

**Goal**  
Validate supplier report for purchasing decisions.

**Steps**

1. Create template:
   - Scope = `Supplier / Price Analysis`
   - Output Format = `Excel`
   - From Date = today - 12 months
   - To Date = today
2. Generate without email.
3. Download and inspect file.

**Expected**

- Rows by supplier/article.
- Includes line count, average price, purchased qty, conformity status.

**Failure checks**

- Empty output: verify price history exists in period.
- Wrong averages: verify source prices and quantities.

---

## S4 - Combined report margin + article/supplier

**Goal**  
Validate multi-dimension combined analysis and CSV export.

**Steps**

1. Create template:
   - Scope = `Article Consumption by Site & Supplier`
   - Output Format = `CSV`
2. Generate report.
3. Download and open CSV in Excel.

**Expected**

- Contains Site, Article, Supplier, Planned, Actual, Variance.
- Values match source consumptions.

**Optional extension**

- Create second template with scope `Net Margin by Salesperson & Client` for management control.

---

## S5 - Monthly automation to management

**Goal**  
Validate scheduled monthly automatic generation and dispatch.

**Steps**

1. Create template:
   - Scope = `Net Margin & Article Consumption` (or `Consolidated Margin` for multi-company)
   - Schedule = `Monthly`
   - Recipients = general management users
2. Save.
3. Trigger scheduled action manually:
   - `Settings -> Technical -> Automation -> Scheduled Actions`
   - Run `BTP Reports: Scheduled Report Generation`
   - **Note:** Monthly (and weekly) templates run when due by calendar *or* when they have no export in the last 31 days (monthly) / 8 days (weekly). So a new monthly template will run on first manual cron trigger and create an Export History row.
4. Re-open template and export history.

**Expected**

- New export job exists with `Done`.
- Email sent to recipients with attached report.

**Pass/Fail**

- Pass only if automation creates job and sends email without manual generation button.

---

## 8) Manual Validation Checklist (All features)

- Template can be created/edited with all filters.
- Every required format (`PDF`, `Excel`, `CSV`) generates valid files.
- Export history correctly tracks `pending/done/failed`.
- Download action works for successful jobs only.
- Scheduled cron runs and generates due templates.
- Weekly logic = Monday; monthly logic = day 1.
- Company-scoped recipients are respected.
- Combined scopes return coherent data (not empty due to domain mistakes).

---

## 9) Troubleshooting Matrix

| Problem | Root cause to check | Corrective action |
| --- | --- | --- |
| Export job = Failed | Scope method raises error, missing model data | Open `error_message`; validate source data and filters |
| Excel export fails | Missing `xlsxwriter` dependency | Install `xlsxwriter` or switch to CSV |
| No email received | Recipient has no email / mail server issue | Check user email + outgoing SMTP + mail queue |
| Scheduled run not triggering | Cron inactive or not due | Activate cron; run manually. Monthly runs on 1st or if no export in 31 days; weekly on Monday or no export in 8 days |
| Export History empty after manual cron | Template was not “due” (e.g. monthly only on 1st) | Logic now treats “no recent export” as due: run cron again; new monthly templates run on first trigger |
| Empty report | Filters too restrictive (date/company/geography) | Clear filters and rerun |
| PDF not generated | QWeb report template issue | Verify generic report XML loaded, upgrade module |

---

## 10) Final Sign-off

Use this sign-off table for client acceptance:

| Scenario | Tester | Date | Result | Notes |
| --- | --- | --- | --- | --- |
| S1 Commercial weekly Excel email |  |  | Pass/Fail |  |
| S2 Site PDF export |  |  | Pass/Fail |  |
| S3 Supplier 12-month analysis |  |  | Pass/Fail |  |
| S4 Combined CSV analysis |  |  | Pass/Fail |  |
| S5 Monthly automation |  |  | Pass/Fail |  |

Module 11 is accepted only when all scenarios pass and no failed export remains unresolved.

