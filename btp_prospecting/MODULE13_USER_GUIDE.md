# Module 13 — Multi-companies

## 1) Objectives & Scope

Module 13 enables several group companies to operate in one Odoo with:

- strict company-based visibility for operational data,
- controlled sharing for strategic records (clients, suppliers, articles, leads),
- company-specific business conditions where needed,
- consolidated management reporting (turnover, cash, margin, shared clients).

This document is both a user guide and UAT checklist.

---

## 2) Requirement-to-Implementation Matrix

| Requirement | Status | Implementation |
| --- | --- | --- |
| Company selection and switch | Implemented | Odoo multi-company selector + allowed company rights |
| Each document attached to one company | Implemented | `company_id` on lead/order/invoice/site |
| Shared vs exclusive data behavior | Implemented/Improved | shared clients/leads fields + stricter rules; company flags in `res.company` |
| Shared client with per-company conditions | Implemented/Improved | `btp.company.commercial.condition` + uniqueness + validation |
| Shared lead visibility across companies | Implemented | `sharing_type`, `shared_company_ids`, multi-company lead rule |
| Consolidated multi-company reports | Implemented/Improved | turnover/cash/margin/shared-client scopes + HT corrections + period filter on margin |
| Group vs single-entity filtering in reports | Implemented/Improved | report `company_id` filter + consolidation actions default to group scope |

---

## 3) Menus, Models, and Key Fields

### 3.1 Menus

- `BTP Prospecting -> Multi-companies -> Company Sharing Settings`
- `BTP Prospecting -> Multi-companies -> Consolidation Reports`

### 3.2 Main Models

- `res.company` (extended): company sharing policy + SIREN
- `res.partner` (extended): shared companies and company-specific commercial conditions
- `btp.company.commercial.condition`: one condition per client/company
- `btp.lead` (extended): multi-company sharing type and shared companies
- `btp.report.template`: consolidation scopes

### 3.3 Key Fields

- **Company policy**: `btp_siren`, `btp_shared_clients`, `btp_shared_suppliers`, `btp_shared_articles`
- **Partner sharing**: `btp_shared_company_ids`
- **Commercial condition**: `partner_id`, `company_id`, `pricelist_id`, `payment_term_id`, `incoterm_id`
- **Lead sharing**: `sharing_type` (`exclusive` / `shared` / `global`), `shared_company_ids`
- **Document flags**: `sale.order.btp_is_shared`, `project.project.btp_is_shared`

---

## 4) Access and Separation Rules

- users only see companies in their allowed companies.
- documents remain attached to one company (`company_id`).
- partner visibility is now company/share-aware for salesperson, non-sales, and manager roles.
- commercial conditions are company-scoped and constrained by sharing logic.

Important:
- `BTP Commercial Condition` now enforces one row per `(client, company)`.
- a commercial condition company must match the partner shared-company list when sharing is used.

---

## 5) Shared/Exclusive Data Rules

### 5.1 Exclusive Data

- accounting entries, invoices, payments, bank statements
- sites/contracts and most operational records
- user-level activities scoped by company permissions

### 5.2 Shared Data

- **Clients**: one legal file can be shared by multiple companies, with separate commercial conditions.
- **Suppliers/Articles**: sharing policy controlled by company flags.
- **Leads**: a lead can be shared with several companies through `sharing_type='shared'`.

---

## 6) Consolidation Reports (Module 13)

Available scopes:

- `Consolidated Turnover by Company` (HT basis)
- `Consolidated Cash / Invoiced by Company` (HT basis)
- `Consolidated Net Margin by Company & Site`
- `Shared Clients Distribution`

Improvements applied:

- turnover and cash consolidate on untaxed amounts (`HT` consistency),
- consolidated margin supports period filtering using site reference dates,
- consolidation action defaults to group context (`company_id` empty).

---

## 7) Step-by-Step UAT Scenarios

## S1 — Restricted access (FR user cannot access BE)

Goal:
Validate company perimeter and visibility restrictions.

Steps:
1. Create/choose user with allowed companies = FR only.
2. Login and check company switcher.
3. Open leads/partners/documents list and test BE data access.

Expected:
- BE company not available in selector.
- BE-only data not visible/accessible.

Failure checks:
- user still has BE in allowed companies,
- global/admin groups assigned unintentionally.

## S2 — Shared client with distinct FR/BE conditions

Goal:
Validate shared legal record + separate business conditions.

Steps:
1. Open client company (e.g., Bouygues Construction).
2. Set `Shared Companies` = FR, BE.
3. In Commercial Conditions, add one row for FR and one for BE.
4. Save and create one quote in FR and one in BE for the same client.

Expected:
- one legal file (same partner),
- one condition row per company (duplicates blocked),
- quote in each company uses that company's condition (pricelist/payment term/incoterm when defined).

Failure checks:
- duplicate company condition row accepted (should fail),
- condition company not in shared list (should fail).

## S3 — Shared article with company-specific pricing context

Goal:
Validate shared article usage with company-specific conditions.

Steps:
1. In `Multi-companies -> Company Sharing Settings`, open FR and BE:
   - enable `Use Shared Articles` on both companies,
   - save both records.
2. Open `Quotes & Articles -> Articles` and create or edit the article (example: Fireproof mortar):
   - keep one single catalog record,
   - ensure article is not restricted to one company only (shared usage).
3. Configure selling context:
   - create one pricelist/rule set for FR and one for BE,
   - set different prices for the same article (example FR 10, BE 12).
4. (Optional purchasing-side check) configure supplier or cost context per company for the same article.
5. Switch current company to FR:
   - create quote Q-FR, add the article, note price and conditions.
6. Switch current company to BE:
   - create quote Q-BE, add the same article, note price and conditions.
7. Compare Q-FR vs Q-BE.

Expected:
- same article catalog record can be used,
- company-specific business context can differ by entity.
- Q-FR and Q-BE show different commercial values when configured differently (price, terms, supplier context).

Failure checks:
- company policy flags disabled while expecting shared behavior.
- article accidentally company-restricted (visible only in one entity).
- both companies using same pricelist unintentionally (no price difference).

Pass/Fail:
- Pass only if FR and BE can both use the same article record and obtain distinct configured context.

## S4 — Shared lead, separate company exploitation

Goal:
Validate shared lead visibility and per-company processing capability.

Steps:
1. Switch to FR and create a new lead L-INTL:
   - fill mandatory fields,
   - set `Company = FR`.
2. On the same lead:
   - set `Sharing Type = Shared`,
   - set `Shared Companies = FR, BE`,
   - save.
3. Still in FR:
   - create one activity/follow-up note (FR context evidence).
4. Switch current company to BE and open leads:
   - search L-INTL and open it,
   - verify BE user can read and update allowed fields,
   - create a BE-specific activity/follow-up note.
5. Switch back to FR and verify both traces are visible on the same shared lead record.

Expected:
- same lead is visible in FR and BE according to sharing,
- each company team can process and create activities from its own context.
- no duplicate lead creation required for cross-company exploitation.

Failure checks:
- missing company in `Shared Companies`,
- lead user/company rights preventing access.
- sharing type left as `exclusive` (BE cannot see lead).

Pass/Fail:
- Pass only if BE can access and process the FR-origin lead after sharing setup, and both teams keep traceability on one lead.

## S5 — Group consolidation then entity detail

Goal:
Validate consolidated management view and per-entity drilldown.

Steps:
1. Open `Multi-companies -> Consolidation Reports`.
2. Create template T-GROUP:
   - `Scope = Consolidated Turnover by Company`,
   - set `From Date` / `To Date` for a known period,
   - leave `Company` empty (group mode),
   - `Output Format = Excel`,
   - run `Generate (no email)`.
3. Open Export History and download T-GROUP file.
4. Duplicate template as T-FR:
   - set `Company = FR`,
   - keep same dates,
   - run `Generate (no email)`.
5. Download T-FR file and compare with T-GROUP:
   - T-GROUP must include multi-company rows + consolidated total,
   - T-FR must only include FR.
6. Repeat same check for:
   - `Consolidated Cash / Invoiced by Company`,
   - `Consolidated Net Margin by Company & Site`,
   - optional: `Shared Clients Distribution`.

Expected:
- first report shows all company rows + consolidated total,
- second report restricted to FR,
- amounts consistent with HT definition.
- export history contains successful jobs with downloadable files for each run.

Failure checks:
- date filters too restrictive,
- no posted/in-scope source documents.
- wrong company selected in template (not empty for group run).

Pass/Fail:
- Pass only if group templates consolidate correctly and company-filtered templates show entity-specific detail with coherent totals.

---

## 8) Troubleshooting Matrix

| Problem | Root cause to check | Corrective action |
| --- | --- | --- |
| User sees wrong company data | Allowed companies / group rights mismatch | Review user allowed companies and BTP group memberships |
| Shared client not visible in another company | Partner shared companies not set | Add target company in `Shared Companies` |
| Cannot save commercial condition | Duplicate company line or invalid shared-company mapping | Keep one condition per company and align with shared list/policy |
| Quote does not pick expected conditions | Missing condition row for `(client, company)` | Create/update `btp.company.commercial.condition` line |
| Consolidated report seems wrong | Expecting HT but comparing TTC, or bad date scope | Validate source amounts and date filters |
| Consolidated margin empty | No qualifying sites in period/company | Check site dates and selected company filter |

---

## 9) Final Validation Checklist

- Company switcher only shows allowed companies.
- Core records remain company-bound (`company_id`).
- Shared client behavior works with strict per-company conditions.
- Commercial condition uniqueness and consistency checks are enforced.
- Shared leads are visible according to sharing settings.
- Consolidation reports produce coherent company + group totals.

---

## 10) Sign-off Table

| Scenario | Tester | Date | Result | Notes |
| --- | --- | --- | --- | --- |
| S1 restricted access |  |  | Pass/Fail |  |
| S2 shared client + conditions |  |  | Pass/Fail |  |
| S3 shared article usage |  |  | Pass/Fail |  |
| S4 shared lead exploitation |  |  | Pass/Fail |  |
| S5 consolidation |  |  | Pass/Fail |  |

