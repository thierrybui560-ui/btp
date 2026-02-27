# Module 11 — Reports & Exports — User & Testing Guide

This guide helps you **test Module 11 manually**: where to find report templates, how to generate and export reports (PDF, Excel, CSV), and how to schedule and send them by email. It is based on the current BTP Prospecting implementation (Odoo 19).

---

## 1. What Module 11 Does (Summary)


| Goal                     | What the system does                                                                                                                                                                    |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Report templates**     | Define reusable reports with scope (e.g. Leads & Quotes by Salesperson, Site Progress, QHSE Incidents), period/company filters, output format (PDF, Excel, CSV), and optional schedule. |
| **On-demand generation** | Run a report from its form (Generate / Generate and Send by Email); file is created and stored; optionally emailed to selected users.                                                   |
| **Export history**       | Each run creates an Export Job (run date, status, download link); history is visible per template and in the global Export History list.                                                |
| **Scheduled reports**    | Daily, weekly, or monthly: a cron runs due templates and sends the generated file by email to the template’s recipients.                                                                |
| **Formats**              | PDF (QWeb), Excel (.xlsx, requires `xlsxwriter`), CSV (UTF-8 with BOM for Excel).                                                                                                       |


---

## 2. Feature List (What You Can Test)


| #   | Feature                                                                                      | Where to test                                                            | Section |
| --- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ------- |
| F1  | **Create report template** — Name, scope, format, filters, recipients                        | Reports & Exports → Report Templates → New                               | 5.1     |
| F2  | **Generate report (no email)** — PDF/Excel/CSV, download from Export Job                     | Template form → Generate (no email)                                      | 5.2     |
| F3  | **Generate and send by email** — Same + email to recipients                                  | Template form → Generate and Send by Email                               | 5.3     |
| F4  | **Export History** — List of runs, status, download                                          | Reports & Exports → Export History                                       | 5.4     |
| F5  | **Scheduled reports** — Daily / Weekly / Monthly; cron sends email                           | Template: Schedule = Daily/Weekly/Monthly; wait for cron or run manually | 5.5     |
| F6  | **Scopes** — Commercial, Site, Client, Salesperson, Article, Supplier, QHSE, Margin combined | Template form → Scope                                                    | 4       |


---

## 3. Where to Find Everything (UI Navigation)

### 3.1 BTP menu: Reports & Exports


| Menu path                                                  | What you see                                      | Access                                                        |
| ---------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------- |
| **BTP Prospecting → Reports & Exports → Report Templates** | List and form of report templates.                | BTP Salesperson+ (create/run); Manager/Admin delete.          |
| **BTP Prospecting → Reports & Exports → Export History**   | All export jobs (report, date, status, download). | BTP Salesperson+ (read/create via run); Manager/Admin delete. |


### 3.2 From a report template


| Where                                          | What                                                                  |
| ---------------------------------------------- | --------------------------------------------------------------------- |
| Template form → **Generate and Send by Email** | Generates report, creates Export Job, sends file to Email Recipients. |
| Template form → **Generate (no email)**        | Generates report and creates Export Job; no email.                    |
| Template form → **Exports** stat button        | Opens Export History filtered by this template.                       |
| Template form → **Export History** tab         | Inline list of export jobs for this template.                         |


### 3.3 Access rights

- **Report template**: Salesperson read/create/write; Manager/Admin can delete.
- **Export job**: Salesperson read/create/write (from running a template); Manager/Admin can delete.

---

## 4. Report Scopes (Data Included)


| Scope                                | Content                                                                  |
| ------------------------------------ | ------------------------------------------------------------------------ |
| **Leads & Quotes by Salesperson**    | Quotes count, converted, total amount, leads converted per salesperson.  |
| **Site Progress, Costs & Margins**   | Per site: quote total, invoiced, actual costs, net margin, margin %.     |
| **Business Volume by Client**        | Orders count and total amount per client (partner).                      |
| **Salesperson Activity**             | Leads, converted, quotes won, conversion % per user.                     |
| **Article Consumption**              | Site, article, planned/actual quantity, variance, overconsumption alert. |
| **Supplier / Price Analysis**        | Supplier, article, date, price, quantity from price history.             |
| **QHSE Incidents by Site**           | Site, date, type, status, description (truncated).                       |
| **Net Margin & Article Consumption** | Same as Site Progress (net margin by site).                              |


Filters (optional): **From Date**, **To Date**, **Company**. Empty = no filter (all data).

---

## 5. Step-by-Step Tests

### 5.1 Create a report template (F1)

**Steps**

1. **BTP Prospecting → Reports & Exports → Report Templates** → **New**.
2. **Report Name** = e.g. "Weekly commercial activity".
3. **Scope** = Leads & Quotes by Salesperson.
4. **Output Format** = PDF, Excel, or CSV.
5. **Schedule** = Manual only (or Daily / Weekly / Monthly).
6. Optionally set **From Date** / **To Date**, **Company**, and **Email Recipients**.
7. Save.

**Expected**

- Template is saved; Exports count = 0 until first run.

### 5.2 Generate report (no email) (F2)

**Steps**

1. Open the template created above.
2. Click **Generate (no email)**.
3. You are redirected to the new **Export Job** form.

**Expected**

- Export Job: Status = Done, **Generated File** set, **Run Date** = now.
- Click **Download** to get the file (PDF, .xlsx, or .csv).
- On the template, **Exports** stat button shows 1; Export History tab lists the job.

### 5.3 Generate and send by email (F3)

**Steps**

1. On the template, set **Email Recipients** to one or more users with email addresses.
2. Click **Generate and Send by Email**.
3. Open the new Export Job; confirm Status = Done.

**Expected**

- Report is generated; an email with the file attached is sent to each recipient (check their inbox).

### 5.4 Export History (F4)

**Steps**

1. **Reports & Exports → Export History**.
2. Filter by template, status, or date if needed.
3. Open a job with Status = Done and click **Download**.

**Expected**

- List shows all runs; download works for successful jobs.

### 5.5 Scheduled reports (F5)

**Steps**

1. Create or edit a template: **Schedule** = Daily (or Weekly / Monthly), set **Email Recipients**.
2. Save. The cron **BTP Reports: Scheduled Report Generation** runs once per day (default).
3. **Daily**: every day; **Weekly**: Mondays; **Monthly**: 1st of the month.
4. When due, the report is generated and sent to recipients; a new Export Job is created.

**Expected**

- On the due date (after cron run), new Export Job appears and recipients receive the email. Check **Export History** and mail logs if needed.

---

## 6. Export Formats


| Format    | File type | Notes                                                                                                       |
| --------- | --------- | ----------------------------------------------------------------------------------------------------------- |
| **PDF**   | .pdf      | Table report with title and headers; uses QWeb.                                                             |
| **Excel** | .xlsx     | Table in first sheet. Requires Python library `xlsxwriter` (`pip install xlsxwriter`). If missing, use CSV. |
| **CSV**   | .csv      | UTF-8 with BOM; open in Excel or any spreadsheet.                                                           |


---

## 7. Acceptance Scenarios (Spec Module 11)

### S1 — Commercial report (weekly, Excel, email)

1. Create template: Name = "Leads & Quotes by Salesperson", Scope = Leads & Quotes by Salesperson, Format = Excel, Schedule = Weekly, Recipients = management user(s). Save.
2. Click **Generate and Send by Email**.
3. **Verify**: Export Job Done; recipients receive email with .xlsx attachment; file contains salesperson, quotes, converted, total amount, leads converted.

### S2 — Site report (PDF, share with client)

1. Create template: Scope = Site Progress, Costs & Margins, Format = PDF. Save.
2. **Generate (no email)** → Download the PDF from the Export Job.
3. **Verify**: PDF shows site code, name, quote total, invoiced, costs, net margin, margin %.

### S3 — Supplier report (Excel, 12 months)

1. Set **From Date** = 12 months ago, **To Date** = today on a template; Scope = Supplier / Price Analysis, Format = Excel. Save.
2. **Generate (no email)** → Download.
3. **Verify**: Rows show supplier, article, date, price, quantity for the period.

### S4 — Combined report (margin + consumption, CSV)

1. Create template: Scope = Net Margin & Article Consumption (or Site Progress), Format = CSV. Save.
2. **Generate (no email)** → Download CSV.
3. **Verify**: CSV opens in Excel; columns = Site, Quote Total, Invoiced, Costs, Net Margin, Margin %.

### S5 — Automation (monthly, general management)

1. Create template: Scope = e.g. Site Progress or Net Margin & Article Consumption, Schedule = Monthly, Recipients = general management users. Save.
2. **Verify**: On the 1st of the next month (after cron run), Export History shows a new job and recipients receive the report by email.

---

## 8. Troubleshooting


| Problem                      | What to check                                                                                                                                          |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Report generation failed** | See Export Job **Error** field. Typical: wrong scope implementation, missing data, or (Excel) missing `xlsxwriter`.                                    |
| **Excel format error**       | Install: `pip install xlsxwriter`. Use CSV if you cannot install it.                                                                                   |
| **PDF template not found**   | Module data must load `btp_report_generic_reports.xml` and `btp_report_generic_templates.xml`. Upgrade the module.                                     |
| **No email received**        | Check recipient user has **Email** set; check mail queue and server logs; ensure cron ran (Settings → Technical → Automation → Scheduled Actions).     |
| **Scheduled report not run** | Cron "BTP Reports: Scheduled Report Generation" must be active; Daily = every day, Weekly = Monday, Monthly = 1st. Run the cron manually once to test. |
| **Export History empty**     | Run a report from the template (Generate or Generate and Send by Email) at least once.                                                                 |


---

## 9. Quick Reference — Key Fields


| Model                   | Field              | Meaning                                                                                                                                                                  |
| ----------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **btp.report.template** | name               | Report name.                                                                                                                                                             |
| **btp.report.template** | scope              | commercial_leads_quotes / site_progress / client_volume / salesperson_activity / article_consumption / supplier_analysis / qhse_incidents / margin_consumption_combined. |
| **btp.report.template** | date_from, date_to | Optional period filter.                                                                                                                                                  |
| **btp.report.template** | company_id         | Optional company filter.                                                                                                                                                 |
| **btp.report.template** | output_format      | pdf / xlsx / csv.                                                                                                                                                        |
| **btp.report.template** | schedule           | none / daily / weekly / monthly.                                                                                                                                         |
| **btp.report.template** | recipient_user_ids | Users who receive the report by email when run or scheduled.                                                                                                             |
| **btp.export.job**      | report_template_id | Template used.                                                                                                                                                           |
| **btp.export.job**      | run_date           | When the report was run.                                                                                                                                                 |
| **btp.export.job**      | state              | pending / done / failed.                                                                                                                                                 |
| **btp.export.job**      | attachment_id      | Generated file (PDF/Excel/CSV).                                                                                                                                          |
| **btp.export.job**      | error_message      | Error text if state = failed.                                                                                                                                            |


---

## 10. Summary Checklist

- Report templates are under **Reports & Exports → Report Templates**; create with scope, format, optional schedule and recipients.
- **Generate (no email)** and **Generate and Send by Email** create an Export Job and (for the second) send the file to recipients.
- **Export History** lists all runs; download from the job form when Status = Done.
- Scheduled reports run via cron (daily / weekly / monthly); set Schedule and Email Recipients.
- Use CSV if Excel is not available (no xlsxwriter); PDF uses the generic QWeb report.

