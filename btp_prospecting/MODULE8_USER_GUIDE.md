# Module 8 — Payments & Finances Follow-up

This guide describes **BTP Payments & Finances**: client and supplier payment follow-up, cash forecasts, analytical margins by site, and how they fit with multi-company and existing BTP features.

---

## 1) Objectives & Scope

- **Client payments follow-up**: Outstanding customer invoices (HT/TTC, issue date, due date, paid amount, balance) with color codes for quick reading.
- **Supplier and subcontractor payments follow-up**: Vendor bills with due date, status (paid, pending, late), and optional link to site.
- **Financial forecasts**: Cash plan built from planned client invoices and supplier invoices (inflows/outflows by period), with filters by site and company.
- **Analytical analysis & margins**: Per-site view of quote total (forecast), actual costs (consumptions), invoiced total, and net margin (forecast vs actual).
- **Banking**: Use Odoo’s standard **Invoicing** (or **Accounting**) app for bank statements (OFX/CSV), reconciliation, and cash status.
- **Multi-company**: Each company has its own accounting; BTP lists and forecasts can be filtered by company; use Odoo’s company selector for consolidated views.

---

## 2) Where to Find Module 8 in the UI

- **BTP Prospecting → Payments & Finances**
  - **Bank & Journals**: Opens the accounting journal dashboard (cards for **Bank**, Cash, Sales, Purchase). Click a **Bank** journal card to open it; from there use **Statements** for bank statements and reconciliation. This is where Bank appears—not in the "Dashboards" app (see below).
  - **Import Bank Statement (CSV)**: Wizard to upload a CSV file (date, amount or debit/credit, optional label) and create a bank statement with lines. Also available from the **Bank Statements** list via **Action** → **Import Bank Statement (CSV)**.
  - **Client Outstanding**: List of customer invoices with amounts and due dates. Use the **New** button on this list to create a customer invoice (opens the invoice form, not a journal entry). No default filter (use “To pay” filter if you want only unpaid).
  - **Supplier Outstanding**: List of vendor bills with status and due dates. Use the **New** button on this list to create a vendor bill (opens the bill form, not a journal entry).
  - **Cash Forecast**: Wizard to generate inflows/outflows by day, week, month, or quarter.
  - **Margin by Site**: List of sites with quote total, invoiced total, actual costs, and net margin.
- **Site form → Situations & Invoicing tab**: Section **Margin (forecast vs actual)** with quote total, invoiced total, actual costs, net margin, and margin %.
- **Where is Bank?** The **Dashboards** app (Dashboards → FINANCE → Invoicing) does not show Bank. For **Bank** (statements, import): use **Payments & Finances → Bank & Journals** (above), or **Invoicing** app → **Dashboard**, or **Configuration** → **Accounting** → **Journals** → open a **Bank** journal.

---

## 3) Prerequisites

- **Invoicing** (or **Accounting**) app installed (Module 7 and 8 depend on it).
- For **margins**: Sites with a **Source Quote/Order**, and optionally **Consumptions** (actual quantities) and **Pointing** for cost calculation.
- For **cash forecast**: Customer and/or vendor invoices with **Due date** set (draft or posted).
- **Supplier Outstanding / Vendor bills**: The company must have a **Purchase** journal (and, if you see an error about “general”, a **Miscellaneous** journal). See **Section 3.1** below if the list is empty or “New” raises a journal error.

### 3.1) Supplier Outstanding: empty list or “No journal could be found” (general / purchase)

**Is it expected that Supplier Outstanding has no rows?**  
Yes, if there are no vendor bills (supplier invoices) yet. The list shows only moves of type **Vendor Bill** (`in_invoice`) for the selected company. If you have never created or imported any vendor bill, the list will be empty.

**“No journal could be found in company BTP France for any of those types: general” (or “purchase”)**  
This means the company (e.g. **BTP France**) has no journal of the type Odoo needs to create a new vendor bill:

- For **Vendor Bills**, Odoo needs a **Purchase** journal.
- In some cases the message refers to a **Miscellaneous (general)** journal.

In the database, **BTP France** currently has only one journal: **Customer Invoices** (type **Sale**). There is no **Purchase** journal and no **Miscellaneous** journal for that company. So:

1. **Empty Supplier Outstanding** is expected until you have at least one vendor bill.
2. **“New” fails** until you create the missing journal(s) for that company.

**How to create the missing journal(s) for BTP France**

1. Switch to company **BTP France** (company selector in the top bar).
2. Go to **Invoicing** → **Configuration** → **Journals** (or **Accounting** → **Configuration** → **Journals**, depending on your apps).
3. Click **New**.
4. Create a **Purchase** journal (needed for vendor bills):
   - **Name**: e.g. “Vendor Bills - BTP France”.
   - **Type**: **Purchase**.
   - **Code**: e.g. `BILL` or `INV2`.
   - Save. Odoo may create or link the required accounts (e.g. payables, expenses) for the company.
5. If the error mentioned **general**: create a **Miscellaneous** journal as well:
   - **Type**: **Miscellaneous**.
   - **Code**: e.g. `MISC`.
6. Return to **BTP Prospecting** → **Payments & Finances** → **Supplier Outstanding** and click **New** again; you should be able to create a vendor bill.

### 3.2) Vendor bill: Account field shows only “Create…” (no list of accounts)

**Is it expected?** No. Normally the **Account** field on an invoice line shows a list of accounts (e.g. expense accounts for vendor bills). If you only see **“Create…”**, the company has **no accounts that are valid for invoice lines**: Odoo only allows accounts that are **not** “Receivable”, “Payable”, or “Off-balance” (so you need at least one **Expense** account for vendor bill lines).

**What to do**

1. Switch to company **BTP France** (if that’s the company on the bill).
2. Go to **Invoicing** → **Configuration** → **Chart of Accounts** (or **Accounting** → **Configuration** → **Chart of Accounts**, depending on your apps).
3. Either **load a full chart of accounts** for the company (if you never did: use the CoA wizard or install a localization that creates the chart), or **create one expense account** manually:
   - Click **New**.
   - **Name**: e.g. “Purchases” or “External expenses”.
   - **Code**: e.g. `600000` or `601000`.
   - **Type**: **Expense** (or “Purchases” depending on your CoA).
   - **Company**: BTP France. Save.
4. Optionally set this account as the company’s **Default expense account** (**Invoicing** or **Accounting** → **Configuration** → **Settings** → Company, or the company form).
5. Reopen your draft bill (or create a new one). On the **Invoice Lines** tab, click **Account**: you should now see the new expense account(s). **Use an Expense account** (not “Vendor / Payable” and not “Current Assets” for a normal purchase line). Then set **Due date** on the bill, Save, and **Confirm**.

---

## 4) Payments Follow-up

### 4.1) Clients

1. Go to **BTP Prospecting → Payments & Finances → Client Outstanding**.
2. The list shows customer invoices (posted or draft). There is **no default “To pay” filter**; apply it from the search bar if you want only unpaid invoices.
3. The list displays:
   - **Name**, **Customer**, **Invoice Date**, **Due Date**
   - **Amount Untaxed (HT)**, **Amount Total (TTC)**, **Balance Due**
   - **Payment Status** (Not paid, Partial, Paid, In payment)
4. **Color codes** (if enabled in the view):
   - **Green**: Paid
   - **Orange**: Unpaid or partial (attention)
5. To **create a new customer invoice**, click the **New** button on the Client Outstanding list (this opens the correct invoice form, not a journal entry).
6. Use the **column selector** to show **BTP Site** or **BTP Number**.
7. Use **Filters** (e.g. To pay, By partner, By company) to focus on due or overdue invoices.
8. **Reminders** for BTP site invoices are handled by **Module 7** (automatic reminders D-7, D0, D+15, D+30, formal notice).

### 4.2) Suppliers & Subcontractors

1. Go to **BTP Prospecting → Payments & Finances → Supplier Outstanding**.
2. The list shows vendor bills (in_invoice) with:
   - **Name**, **Vendor**, **Invoice Date**, **Due Date**
   - **Amount Total**, **Balance**, **Payment Status**
3. **Color codes**: Green = paid, Orange = unpaid/partial.
4. Use filters to see **invoices nearing due date** (e.g. due within 7 days) for proactive management.
5. **Payment mode** (transfer, check, LCR, etc.) is managed on the payment when you register the payment from the bill (standard Odoo).
6. Optionally link a vendor bill to a **BTP Site** (field **Site** on the bill) for site-based reporting.

**Ways to add vendor bills**

- **Create a bill manually**: On **Supplier Outstanding**, click the **New** button to open the vendor bill form (Vendor, Bill Date, Due Date, Currency, invoice lines). Enter details, add lines (product/service, quantity, price), then Save and Post. The company must have a **Purchase** journal (see section 3.1 if you get a “No journal could be found” error).
- **Drag & drop / Upload**: Use **Upload** (or drag and drop a PDF/image of the bill onto the list or form). Odoo can create a draft vendor bill from the file and, with the right app (e.g. **Documents** or **Account**), may help prefill data or attach the file to the bill.
- **Create from purchase order**: If you use **Purchase**, create a vendor bill from a confirmed purchase order (Receive products → Create Bill). The bill then appears in Supplier Outstanding.

**List actions**

- Use the **column selector** to show **Site** or **Company**.
- Sort by **Due Date** or **Payment Status** to plan payments.
- Open a line to edit the bill (draft) or register payment (posted).

### 4.3) Reminders & Alerts

- **Clients**: See **Module 7** for automatic reminder emails and **Reminder Status** on BTP invoices.
- **Suppliers**: Use **Supplier Outstanding** and sort/filter by **Due Date** to see what is due soon; no automatic email in this module. You can use **Activities** or your own process for internal D-7 alerts.

---

## 5) Financial Forecasts

1. Go to **BTP Prospecting → Payments & Finances → Cash Forecast**.
2. A wizard opens. Set:
   - **From** / **To**: Date range for the forecast.
   - **Group By**: Day, Week, Month, or Quarter.
   - **Site** (optional): Restrict to one site’s invoices.
   - **Company** (optional): Restrict to one company (multi-company).
3. Click **Generate Forecast**.
4. A list of **Forecast lines** appears with, per period:
   - **Period** (label), **Date**
   - **Inflows**: Sum of customer invoice totals (out_invoice) with due date in that period.
   - **Outflows**: Sum of vendor bill totals (in_invoice) with due date in that period.
   - **Balance**: Inflows − Outflows for the period.
   - **Cumulative**: Running balance.
5. **Inflows** = planned client invoices (posted + draft) by due date. **Outflows** = supplier invoices by due date. Expected deposits can be included if they exist as draft/posted invoices with a due date.
6. Use **optional columns** to show **Site** or **Company** when the forecast mixes several sites/companies.

**Requirements covered**: The system consolidates client and supplier due dates in a single forecast table and generates the forecast from issued (and draft) invoices.

---

## 6) Analytical Analysis & Margins

### 6.1) Margin by Site (list)

1. Go to **BTP Prospecting → Payments & Finances → Margin by Site**.
2. The list shows **sites** (projects) with optional columns:
   - **Quote Total (Forecast)**: Total from the **Source Quote/Order** (forecast revenue).
   - **Invoiced Total**: Sum of **posted** customer invoices linked to the site (BTP invoices).
   - **Actual Costs**: From **Consumptions** (actual quantity × product cost). Pointing/labor can be extended later.
   - **Net Margin**: Invoiced Total − Actual Costs.
   - **Margin %**: Net margin as % of Invoiced Total.
3. Use the **column selector** to show or hide these columns.
4. Compare **forecast vs actual** and **net margins by site**; filter by company for multi-company.

### 6.2) Margin on the Site Form

1. Open a **Site** (**Sites & Documents → Sites**).
2. Go to the **Situations & Invoicing** tab.
3. Scroll to the section **Margin (forecast vs actual)**:
   - **Quote Total (Forecast)**: From the linked quote.
   - **Invoiced Total**: Sum of posted BTP invoices for this site.
   - **Actual Costs**: From site consumptions (real qty × product cost).
   - **Net Margin**, **Margin %**.

### 6.3) How Actual Costs Are Computed

- **Actual costs** = sum over all **Consumptions** of the site of (Real quantity × Product cost).
- **Product cost** = product’s **Cost** (e.g. standard price) in Odoo.
- **Pointing** (labor/subcontracting) is not included in actual costs in the current version; it can be added later (e.g. hours × rate).

**Requirements covered**: Forecast vs actual comparison per site; net margin by site and by company (via company filter or multi-company).

---

## 7) Banking Follow-up

There is **no “Bank” tab** in the main menu. Bank statements and import are reached as follows (BTP has no separate banking module).

- **Where to find bank statements and import**
  1. **BTP shortcut (recommended)**: **BTP Prospecting** → **Payments & Finances** → **Bank & Journals**. This opens the journal dashboard (Bank, Cash, Sales, Purchase cards). Click a **Bank** journal card → **Statements** → **Import** (OFX/CSV).
  2. **From the Invoicing app**: If you see **Dashboard** under **Invoicing**, open it and click the **Bank** journal card (or its ⋮ menu) → **Statements** → **Import**.
  3. **Via Configuration**: **Invoicing** (or **Accounting**) → **Configuration** → **Accounting** → **Journals**. Open a journal of type **Bank** (click its name). On the journal form, open **Statements** or use **Import** to add bank statement lines (OFX/CSV).
- **Where is "Import" or "Import Statement"?** In standard Odoo, the **Import** action for OFX/CSV is **not** in the Bank card ⋮ menu until you install an optional app (e.g. **Apps** → search **"Bank Statement Import"** or **"QIF Import"**) and set the Bank journal’s **Bank Feeds** to **File Import** (⋮ → **Configuration** on the Bank card, or open the journal from Configuration → Journals). After that, **Import** may appear on the card, in the ⋮ menu, or on the Bank Statements list. **BTP** provides **Import Bank Statement (CSV)** under **Payments & Finances** (or from the Bank Statements list: **Action** → **Import Bank Statement (CSV)**). Use it to upload a CSV with columns: date, amount (or debit/credit), and optional label.
- **Reconciliation**: From a bank statement (opened as above), match bank lines with invoices/payments (standard Odoo).
- **Real-time cash**: Use **Bank & Journals** (Payments & Finances) or **Configuration** → **Accounting** → **Journals**; open the Bank journal for movements and statement lines.
- **Multi-accounts / multi-companies**: Use the company selector in the top bar; journals are per company.



---

## 8) Multi-company

- **Per company**: Invoices, payments, and bank data are per **Company** (Odoo standard).
- **BTP views**: In **Client Outstanding**, **Supplier Outstanding**, **Cash Forecast**, and **Margin by Site**, you can filter (or show a column) by **Company**.
- **Consolidated group view**: Use the **company selector** in the top bar to switch company, or use **multi-company** filters/grouping in list views where the **Company** column is shown.

---

## 9) Reports & KPIs (summary)

- **Client outstanding**: **Payments & Finances → Client Outstanding** (due invoices, optional filter e.g. delay &gt; 30 days).
- **Supplier outstanding**: **Payments & Finances → Supplier Outstanding** (invoices to pay by due date).
- **Cash forecast**: **Payments & Finances → Cash Forecast** (future balance by period; no graphic in this module; export to spreadsheet if needed).
- **Margin by site**: **Payments & Finances → Margin by Site** (gross/net margin; add **Margin %** column).
- **Company vs group**: Use company filter and optional **Company** column in the above views for comparative consolidated margins.

---

## 10) Acceptance Scenarios (summary)

- **S1 — Site forecast**: Quote 200k€, planned invoicing 50k€/month, planned supplier 30k€/month → use **Cash Forecast** with group by Month to see +20k€/month (inflows − outflows).
- **S2 — Client reminder**: Invoice due 15/04 unpaid → use **Client Outstanding** and **Module 7** automatic reminders and formal notice.
- **S3 — Supplier invoice**: Bill due 30/04 → **Supplier Outstanding** and sort by due date; use filters/activities for D-7 internal alert.
- **S4 — Site margin**: Quote planned 100k€ cost, actual 110k€, invoiced 150k€ → **Margin by Site** (or site form) shows net margin 40k€ vs planned 50k€ (deviation −10k€).
- **S5 — Multi-company**: Companies FR and BE → use company filter and **Company** column in Client/Supplier Outstanding, Cash Forecast, and Margin by Site for consolidated reporting.

---

## 11) Troubleshooting

- **No lines in Cash Forecast**: Check that customer and/or vendor invoices have **Due date** set and fall within the chosen date range; confirm filters (site/company).
- **Margin = 0 or wrong**: Ensure the site has a **Source Quote/Order** (quote total). For **actual costs**, ensure **Consumptions** are entered with **Actual quantity** and that products have a **Cost**.
- **Client/Supplier Outstanding empty**: Check that moves are **Customer Invoices** or **Vendor Bills** and state is **Posted** or **Draft**; check company and search filters.
- **"Even magicians can't post nothing!" when clicking Confirm**: Odoo does not allow posting an invoice or bill that has **no invoice lines** (0.00 € total). Add at least one line (product/service, quantity, price) under **Invoice Lines**, then Save and Confirm.
- **"Any journal item on a payable account must have a due date" (vendor bill)**: (1) The **Account** on each **Invoice Line** must be an **expense** account (e.g. Purchases), not the vendor payable account (e.g. "Vendor - BTP France") and not "Current Assets". (2) Set the bill **Due date** and Save before Confirm. If the **Account** dropdown only shows "Create…", the company has no valid accounts for lines—see **Section 3.2** to add an expense account / chart of accounts.
- **Banking / “Where is Bank?”**: There is no **Bank** tab. Use **BTP Prospecting** → **Payments & Finances** → **Bank & Journals** (then click a Bank journal card → Statements / Import). Or **Invoicing** → **Configuration** → **Accounting** → **Journals**, open a **Bank** journal, then **Statements** and **Import**. Ensure at least one Bank journal exists for your company.
