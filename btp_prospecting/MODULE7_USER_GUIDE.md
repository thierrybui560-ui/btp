# Module 7 — Invoicing & Situations

This guide describes **BTP Invoicing & Situations**: monthly progress situations, retention of guarantee, invoice numbering, and reminder follow-up.

---

## 1) Objectives & Scope

- **Monthly situations**: item-by-item progress (cumulative M, M-1, month progress, balance to invoice).
- **Retention of guarantee**: configurable per site (default 5%), applied to situations; release date tracked.
- **Invoice numbering**: YYYYMMNNN (aligned with quotes); revisions with alphabetical index (A, B, C).
- **Deposit invoicing**: issue a deposit invoice per site; deposits are automatically deducted from subsequent situation invoices.
- **Final invoicing**: for small markets, generate one final invoice from the quote total (one per site).
- **Follow-up**: due date, payment state, reminder status; automatic reminder emails (D-7, D0, D+15, D+30, formal notice).

---

## 2) Where to Find Module 7 in the UI

- **BTP Prospecting → Sites & Documents → Sites**  
  Open a site → **Situations & Invoicing** tab: create situation, create deposit invoice, create final invoice, view situations and invoices.
- **BTP Prospecting → Sites & Documents → Situations**  
  List of all situations (by site, date, status).
- **Invoices** for a site: from the site form, click the **Invoices** stat button (or open an invoice from a situation).

---

## 3) Prerequisites

- A **Site** with a linked **Sale Order** (source quote) and quote items (Lot → Title → Subtitle → Item).
- **Accounting** app installed (Module 7 depends on it).

---

## 4) Monthly Situation (Standard BTP)

1. Open **Sites & Documents → Sites** and open the site.
2. Go to the **Situations & Invoicing** tab.
3. Click **Create situation**. A draft situation is created for the end of the current month, with one line per quote item (global item amount = quote subtotal, cumulative M/M-1 = 0).
4. Edit each line: set **Cumulative at M-1** (previous month cumulative) and **Cumulative at M** (current month cumulative). **Month's Progress** and **Balance to Invoice** are computed.
5. Click **Confirm**.
6. Click **Create Invoice**. A customer invoice is created with:
   - BTP number (YYYYMMNNN) from the BTP invoice sequence
   - One invoice line per situation line (amount = month progress)
   - **Deposit deduction**: if the site has posted deposit invoice(s), an automatic **Deduction of deposit** line (negative amount) is applied up to the situation amount; the remaining deposit is tracked and applied on future situation invoices until exhausted.
   - Retention rate/amount from the site (default 5%)
   - Link to the situation and site
7. Post and send the invoice as usual. The situation state becomes **Invoiced**.

**Site retention**: On the site form, set **Retention Rate %** (default 5) and **Retention Release Date** (e.g. 12 months after reception). Retention amount is stored on the invoice and can be used for reporting.

---

## 4.1) Deposit Invoicing

1. Open the site and go to **Situations & Invoicing**.
2. Click **Create deposit invoice**. Enter the deposit amount (a default of 10% of the quote total is suggested if a quote is linked).
3. Confirm to create a customer invoice with **BTP Invoice Type** = Deposit, linked to the site.
4. Post the deposit invoice. When you later create **situation** invoices for this site, the system will automatically add a **Deduction of deposit** line (up to the situation amount) until the total deposit is fully deducted.

---

## 4.2) Final Invoicing (One-Shot)

For small markets or individual clients, you can issue a single **final invoice** instead of monthly situations:

1. Open the site and go to **Situations & Invoicing**.
2. Click **Create final invoice**. Only one final invoice is allowed per site; the button is hidden once one exists.
3. A customer invoice is created with **BTP Invoice Type** = Final, with one line per quote item (full quote subtotals), retention applied, and linked to the site.
4. Post and send as usual. No monthly situations are required for this site.

---

## 5) Invoice Numbering

- **Format**: YYYYMMNNN (e.g. 202501001 = first invoice of January 2025). Monthly reset to 001.
- **Revisions**: See **5.1** below for how to use the **Revision** field (A, B, C) when you modify or re-issue an invoice.

### 5.1) Using Revisions When Modifying an Issued Invoice

When an invoice has already been issued (posted or sent) and you need to correct it or re-issue it, the BTP spec allows an **alphabetical revision index** (A, B, C…) so you can keep the same BTP number and indicate that the document is a revised version.

**Recommended: “Create revision” (automatic letter)**

1. Open the **posted** BTP invoice (**Sites → Invoices** or from a situation).
2. Click **Create revision** in the header.
3. A **new draft invoice** is created with the **same BTP number**, the **next revision letter** (A, then B, then C…) set **automatically**, and the same lines/amounts (you can edit before confirming).
4. Adjust the draft if needed, then **Confirm** and send. The system ensures you never reuse the same letter (e.g. two “A”s for 202501001).

This avoids choosing the wrong letter and keeps revisions in order (A, B, C…) without manual selection.

**When to use a revision**

- You need to issue a corrected or amended version of an invoice under the same BTP number.
- The customer requested a change and you want to keep one document per BTP number with a clear revision (A, B, C).

**Alternative: Reset to draft or credit note + new invoice**

- **Reset to draft**: If you **Reset to Draft** on the same invoice and edit it, you can set **Revision** from the dropdown (A, B, C…) in the BTP Invoicing block before re-confirming. Use this only when you are sure no other revision with that letter exists for this BTP number.
- **Credit note + new invoice**: If you issue a credit note and then create a new invoice, you can set **Revision** on the new invoice from the dropdown. Prefer **Create revision** when possible so the letter is assigned automatically.

**Revision field behaviour**

- **Best practice:** Use **Create revision** so the next letter (A, B, C…) is **set automatically**; you cannot pick a letter already used for that BTP number.
- **Revision** is a single letter (optional; empty = original). It is **editable only in Draft**; after posting it is locked.
- It is stored on the invoice for reporting and for display on documents (if you include it in your report layout).

---

## 6) Payments and Reminders

- Each invoice has **Due Date**, **Payment Status** (paid / partial / not paid), and **BTP Reminder Status** (None, 1st reminder, 2nd reminder, Formal notice). **Courtesy Reminder Sent** and **Official Reminder Sent** (D-7 and D0) are also stored on the invoice.
- **Where to see Payment Status**: On a BTP invoice, open the form and look at the **BTP Invoicing** section (right column): **Payment Status** is shown there (Not paid, Partial, Paid, etc.). In the invoice list, add the optional column **Payment Status** (via the column selector) to see it for all invoices.
- **Follow-up table**: In the invoice list, use optional columns **Payment Status**, **BTP Invoice Type**, **BTP Number**, **Site**, **Reminder Status**. You can use decorations (e.g. red if late, orange if due soon) in list views.
- **Automatic reminder emails**: A daily cron both updates **Reminder Status** and **sends reminder emails** to the customer (invoice partner) for unpaid BTP site invoices:
  - **D-7**: Courtesy reminder (before due date)
  - **D0**: Official reminder (on due date)
  - **D+15**: 1st reminder
  - **D+30**: 2nd reinforced reminder, then automatic **formal notice** (3rd reminder)
- Email templates are configurable under **Settings** (or via **Email** templates): BTP Invoice Courtesy Reminder, Official Reminder, 1st Reminder, 2nd Reminder, Formal Notice.

---

## 7) Reports & KPIs

- **Invoice status by site**: Open a site → **Invoices** stat button; or filter invoices by **Site** (BTP field).
- **Retention**: On the invoice form, **Retention Rate %** and **Retention Amount**; on the site, **Retention Release Date**.
- **Planned vs actual invoicing**: Use situation lines (total amount, cumul M, balance to invoice) and compare with invoiced amounts.

---

## 8) Acceptance Scenarios (Summary)

- **S1 — Monthly situation**: Create situation for site X for end of January → fill cumul M-1 / cumul M → confirm → create invoice → item-by-item table with progress M and M-1.
- **S2 — Deposit**: Create deposit invoice from site → post → create situation invoice → deposit is automatically deducted (line “Deduction of deposit”).
- **S3 — Final invoice**: Create final invoice from site (one per site) → invoice with quote totals and retention.
- **S4 — Retention**: Site with 5% retention → invoice shows retention amount; release date on site → alert can be configured separately.
- **S5 — Automatic reminders**: Unpaid BTP site invoice → cron sends emails (D-7 courtesy, D0 official, D+15 1st, D+30 2nd and formal notice) and updates reminder status.

---

## 9) Troubleshooting

- **"Link a Source Quote/Order to the site first"**: The site must have **Source Quote/Order** (Sale Order) set.
- **"No income account found"**: Configure a product with an income account, or ensure the company has an account of type **Income**.
- **"BTP invoice sequence is not configured"**: Upgrade the module so that the **BTP Invoice** sequence is created (data file `btp_invoice_sequence.xml`).
