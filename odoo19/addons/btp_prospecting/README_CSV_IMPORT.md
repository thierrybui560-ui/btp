# Bank Statement CSV Import – Format

Use **BTP Prospecting → Payments & Finances → Import Bank Statement (CSV)** (or the **Import (CSV)** button on the Bank Statements list) and upload a CSV file.

## Required columns

| Purpose   | Column name (one of these) |
|----------|-----------------------------|
| **Date** | `date`, `transaction_date`, `value_date`, `booking_date`, or any name containing `date` |
| **Amount** | Either **one** signed column **or** **two** columns: |
|           | **Single column:** `amount`, `montant`, `sum`, `total`, `balance` (positive = inflow, negative = outflow) |
|           | **Two columns:** `debit` and `credit` (amount = credit − debit) |

## Optional column

| Purpose  | Column name (one of these) |
|----------|----------------------------|
| **Label** | `label`, `payment_ref`, `reference`, `libelle`, `name`, `description`, `details`, `memo`, `remark`, etc. |

## Format rules

- **Encoding:** UTF-8 (with or without BOM).
- **Separator:** Comma (`,`) or semicolon (`;`) – auto-detected from the first line.
- **Date format:** e.g. `2025-02-19` (YYYY-MM-DD) or `19/02/2025` (DD/MM/YYYY). If your format differs, set the **Date format** in the wizard (e.g. `%d/%m/%Y`).
- **Amount:** Use a dot for decimals (e.g. `1500.00`). Spaces as thousand separators are removed.
- **Header row:** First row must be column names. Accents (e.g. Débit, Montant) are supported.

## Sample files in this addon

- **sample_bank_statement_import.csv** – one `amount` column (positive = in, negative = out), plus `date` and `label`.
- **sample_bank_statement_debit_credit.csv** – separate `debit` and `credit` columns, plus `date` and `label`.

Copy one of these files, adjust to your data, then import.
