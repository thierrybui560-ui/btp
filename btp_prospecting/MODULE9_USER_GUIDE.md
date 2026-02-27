# Module 9 — Stocks & Logistics — User & Testing Guide

This guide helps you **test Module 9 manually**: where to go in the UI, what data to use, what to do step by step, and what you should see. It is based on the current BTP Prospecting implementation (Odoo 19).

---

## 1. What Module 9 Does (Summary)

| Goal | What the system does |
|------|----------------------|
| **Multi-warehouse** | Manage stock in several warehouses (headquarters, agencies, site depots). |
| **Link stock to sites** | Transfers and moves can be linked to a BTP site; consumptions on site are tracked. |
| **Reservations** | When you confirm a quote with storable products, stock is reserved (standard Odoo + BTP site on moves). |
| **Site consumptions** | Record planned vs actual quantities per site/article; variance and overconsumption alert. |
| **Outbound from consumption** | From a consumption line (storable product), create a stock move to deduct stock and keep traceability. |
| **Traceability** | Moves show BTP Site, BTP Origin (client order, site consumption, transfer, etc.), and optional link to consumption. |

---

## 2. Feature List (What You Can Test)

Use this as a checklist for manual testing.

| # | Feature | Where to test | Section |
|---|---------|----------------|---------|
| F1 | **Site depot location** — Link a stock location to a BTP site | Inventory → Locations; set "Site" (BTP) | 5.1 |
| F2 | **Supplier reception (inflow)** — Receive products; no BTP site on receipt | Purchase → receive; then Transfers / Moves | 5.2 |
| F3 | **Delivery with BTP site** — Confirm order with site → delivery moves get BTP Site + Origin "Client Order" | Quote with site → Confirm → Transfers | 5.3 |
| F4 | **Reservation on order** — Confirm order with storable product and site → delivery created, moves show BTP Site | Same as F3; Check Availability on delivery | 6.1 |
| F5 | **Site consumption (planned vs actual)** — Create consumption; see variance and overconsumption alert | Consumptions → New | 6.2 |
| F6 | **Create outbound move from consumption** — Storable product → button "Create Outbound Move" → move created and linked | Consumption form → Stock section → Create Outbound Move | 6.3 |
| F7 | **Internal transfer to site depot** — Transfer to location with BTP Site; set BTP Origin on move | Transfers → New (Internal) → To = site depot | 5.4 |
| F8 | **Physical inventory** — Count and adjust stock (standard Odoo; optional BTP traceability) | Inventory → Adjustments → Physical Inventory | 7.1 |
| F9 | **Reports** — Stock by location, consumptions by site, moves by BTP Site/Origin | Products (Stock), Consumptions Pivot, Moves | 8 |

---

## 3. Where to Find Everything (UI Navigation)

### 3.1 BTP menu: Stocks & Logistics

| Menu path | What you see | Access |
|-----------|--------------|--------|
| **BTP Prospecting → Stocks & Logistics → Transfers** | All pickings (receipts, deliveries, internal). Column **BTP Site** when linked. | Inventory User |
| **BTP Prospecting → Stocks & Logistics → Moves** | All stock moves. Optional columns **Site**, **BTP Origin**. Filter "BTP Site". | Inventory User |
| **BTP Prospecting → Stocks & Logistics → Consumptions** | Site consumptions (planned/actual, variance, overconsumption). Same as Planning & Yield → Consumptions. | BTP Salesperson+ |
| **BTP Prospecting → Stocks & Logistics → Products (Stock)** | On-hand quantities by product/location (quants). | Inventory User |

### 3.2 Other entry points

| Where | What |
|-------|------|
| **Sites & Documents → Planning & Yield → Consumptions** | Same consumptions list/form; on the form you get the **Stock** section with **Create Outbound Move**. |
| **Inventory app** | Warehouses, Locations, Operations, Products, Reporting. BTP adds **Site** on Locations (site depot) and **BTP Site / BTP Origin** on Moves and Transfers. |
| **Quotes & Articles → Quotes** | Create/confirm orders; link to BTP site so deliveries get BTP Site. |

### 3.3 Access rights

- **Transfers**, **Moves**, **Products (Stock)**: need **Inventory User** (or Manager).  
- **Consumptions**: visible to BTP Salesperson and above.  
- **BTP Site** on locations: visible to BTP users (e.g. Salesperson group).

---

## 4. Mock Data for Testing

Create these once so all steps below are repeatable.

### 4.1 Reference table

| Entity | Field | Value | Notes |
|--------|--------|--------|--------|
| **Company** | Name | My Company | Must have at least one warehouse. |
| **Customer** | Name | Demo Building Corp | For quotes/orders. |
| **Warehouse** | Name | WH | Default warehouse; main stock location e.g. WH/Stock. |
| **Product (storable)** | Name | Fireproof mortar | Type = **Storable**, UoM = kg, Internal Ref = MORTAR-FP. |
| **Product (storable)** | Name | Mineral wool 100mm | Type = **Storable**, UoM = m², Internal Ref = MW-100. |
| **Product (consumable)** | Name | Fixing paste | Type = **Consumable**, UoM = kg, Internal Ref = PASTE-FIX. |
| **Site** | Name | Tour La Défense – Flocking | From quote "Create site" or Sites → New. Must have **Site Code** (e.g. 202501001). |
| **Location (site depot)** | Name | Site 202501001 depot | Usage = Internal, **Site** (BTP) = Tour La Défense – Flocking. |
| **Initial stock** | — | Fireproof mortar **100 kg**, Mineral wool **50 m²** | So reservation tests pass (e.g. via receipt or Update quantity). |

### 4.2 Setup order

1. Create the **3 products** (2 storable, 1 consumable).  
2. Ensure **warehouse** exists (Inventory → Configuration → Warehouses).  
3. Add **initial stock** for the 2 storable products (e.g. 100 kg and 50 m²) via a purchase receipt or Inventory adjustment.  
4. Create **customer** Demo Building Corp.  
5. Create a **quote** with lines using the storable products, then **Confirm** and choose **Create site** so you get site **Tour La Défense – Flocking** with a site code.  
6. **Inventory → Configuration → Locations**: New location **Site 202501001 depot**, Parent = e.g. WH, Usage = Internal, **Site (BTP)** = Tour La Défense – Flocking.

---

## 5. Warehouse & Locations (F1)

### 5.1 Link a location to a BTP site (site depot)

**Steps**

1. **Inventory** → **Configuration** → **Locations** (or open a warehouse and use Locations).  
2. **New**: Name = `Site 202501001 depot`, Parent = your main warehouse (e.g. WH), Usage = **Internal**.  
3. In the **BTP** group, set **Site** = **Tour La Défense – Flocking**.  
4. Save.

**Expected**

- Location form shows **Site** = Tour La Défense – Flocking.  
- In **Stocks & Logistics → Moves**, you can filter by destination = this location to see moves to the site depot.

---

## 6. Logistics Flows

### 6.1 Inflows — Supplier reception (F2)

**Steps**

1. **Purchase** → **New**: Vendor = any supplier; line Product = **Fireproof mortar**, Quantity = 100, Unit Price = 12. Confirm.  
2. **Receive Products** → set Done = 100 for Fireproof mortar → **Validate**.

**Expected**

- **Stocks & Logistics → Transfers**: one receipt; **BTP Site** is empty.  
- **Fireproof mortar** on-hand increases by 100 kg.

### 6.2 Outflows — Delivery linked to BTP site (F3, F4)

**Steps**

1. **Quotes & Articles → Quotes** → **New**.  
2. Customer = **Demo Building Corp**. Add a line: Product = **Fireproof mortar**, Quantity = 20, Unit Price = 15. Save.  
3. **Confirm** the order; when asked to create a site, confirm so **BTP Site** = Tour La Défense – Flocking.  
4. **Stocks & Logistics → Transfers**: open the **delivery** for this order.  
5. **Check Availability** → **Validate**.

**Expected**

- Transfer (delivery) shows **BTP Site** = Tour La Défense – Flocking.  
- Each move has **Site** = Tour La Défense – Flocking, **BTP Origin** = **Client Order**.  
- Fireproof mortar on-hand decreases by 20 kg.

### 6.3 Internal transfer to site depot (F7)

**Steps**

1. **Stocks & Logistics → Transfers** → **New**.  
2. Operation type = **Internal Transfer** (or From = WH/Stock, To = **Site 202501001 depot**).  
3. Add a line: Product = **Mineral wool 100mm**, Demand = 10 m².  
4. In the **Operations** tab on the same transfer form (the list "Stock Moves" with "Add a Product"), set **Site** and **BTP Origin** on the line: **Site** = Tour La Défense – Flocking, **BTP Origin** = **Internal Transfer**. If the **Site** or **BTP Origin** columns are not visible, use the column chooser (➕ or "Columns" at the right of the column headers) and enable them.  
   - **Do not** use the "Moves" / "Detailed Operations" button in the button box — that opens a different view (detailed move lines) where BTP fields are not available.  
5. **Validate**.

**Expected**

- **Stocks & Logistics → Moves**: filter by **BTP Site** = Tour La Défense – Flocking; one move with destination = Site 202501001 depot, **BTP Origin** = Internal Transfer.

---

## 7. Site Consumptions (F5, F6)

### 7.1 Create consumption and see variance / overconsumption (F5)

**Steps**

1. **Stocks & Logistics → Consumptions** (or **Sites & Documents → Planning & Yield → Consumptions**) → **New**.  
2. **Site** = Tour La Défense – Flocking, **Article** = **Fixing paste** (or Fireproof mortar), **Planned Quantity** = 250, **Actual Quantity** = 300.  
3. Save.

**Expected**

- **Variance** = 50 (300 − 250).  
- **Overconsumption Alert** = Yes (toggle on).  
- In list view you can sort/filter by **Overconsumption Alert** to find such lines.

### 7.2 Create outbound move from consumption (F6)

**Steps**

1. **Consumptions** → **New**.  
2. **Site** = Tour La Défense – Flocking, **Article** = **Fireproof mortar** (storable), **Planned Quantity** = 25, **Actual Quantity** = 0 or 25. Save.  
3. On the form, in the **Stock** section (below Variance / Overconsumption Alert), click **Create Outbound Move**.  
4. You are redirected to the new **stock move**. On the move (or via Transfers): **Confirm** → **Validate** (or process the picking).  
5. Reopen the **consumption** record.

**Expected**

- **Stock Move** is filled with the created move.  
- **Actual Quantity** = 25 (updated when the move was validated).  
- **Stocks & Logistics → Moves**: filter **BTP Origin** = **Site Consumption**; one move with **Site Consumption** = your consumption line.

**When the button is hidden / errors**

- **Create Outbound Move** appears in the **Stock** section whenever **Stock Move** is empty. If the article is **Consumable**, the button is still shown but the server will show an error if you click it; use a **Storable** article to deduct stock.

---

## 8. Inventories & Valuation (F8)

### 8.1 Physical inventory

**Steps**

1. **Inventory** → **Adjustments** → **Physical Inventory** (or Count).  
2. Location = WH/Stock (or Site 202501001 depot). Add line: Product = **Fireproof mortar**, **Counted Quantity** = 95 (e.g. if theoretical was 100).  
3. **Apply** / **Validate**.

**Expected**

- An adjustment move is created; **Fireproof mortar** on-hand = 95.  
- Valuation uses Odoo standard (FIFO / standard cost). No BTP-specific change.

---

## 9. Reports & KPIs (F9)

| What you want | Where to go | What to do |
|---------------|-------------|------------|
| **Stock by warehouse/location** | **Stocks & Logistics → Products (Stock)** or Inventory → Reporting | Filter by product/location; use **Site** on locations for site depots. |
| **Reserved vs available** | Product form or Moves list | Standard Odoo **Forecasted** / **Reserved**. |
| **Consumption by site** | **Consumptions** → switch to **Pivot** | Group by **Site** and/or **Article**; measures **Actual Quantity**, **Planned Quantity**, **Variance**. |
| **Moves by site** | **Stocks & Logistics → Moves** | Filter **BTP Site** or group by **BTP Site** / **BTP Origin**. |
| **Stock valuation** | Inventory reporting | Standard valuation report (FIFO/standard). |

---

## 10. UI Guidelines & Expected Behavior

### 10.1 Transfers (pickings)

- **List**: Columns include **Partner**, **Origin**, **BTP Site** (optional; show via column chooser for BTP users).  
- **Form**: After **Origin**, **BTP Site** is shown (from first move with a site).  
- **Behavior**: BTP Site on the transfer is computed from its moves; do not edit it on the transfer, set it on the moves if needed.

### 10.2 Moves

- **List**: Optional columns **Site**, **BTP Origin**.  
- **Search**: Filter **"BTP Site"** = moves that have a site.  
- **Form**: **BTP** group: **Site**, **BTP Origin**, **Site Consumption** (readonly when from consumption).  
- **Behavior**: For deliveries from a sale order with **BTP Site**, moves get Site and Origin = **Client Order** automatically. When a move linked to a consumption is set to **Done**, **Actual Quantity** on the consumption is updated.

### 10.3 Locations

- **Form**: **BTP** group with **Site** (only locations for site depots).  
- **Behavior**: Only projects with **Site Code** appear in **Site**. Moves to/from this location can be reported by site.

### 10.4 Consumptions

- **List**: **Site**, **Task**, **Article**, **Planned Quantity**, **Actual Quantity**, **Unit**, **Variance**, **Overconsumption Alert** (toggle).  
- **Form**: Same fields + **Quote Item**, **Notes**; then **Stock**: **Stock Move** (readonly), button **Create Outbound Move** (when no move linked; storable articles only for deduction).  
- **Behavior**: Variance = Actual − Planned; Overconsumption Alert = True when Planned > 0 and Variance > 0.  
- **Create Outbound Move**: Creates a move (warehouse stock → site depot or scrap), sets **BTP Origin** = Site Consumption and links **Site Consumption** to this line. After the move is **Done**, **Actual Quantity** is set from the move.

### 10.5 BTP Origin values

| Value | Meaning |
|-------|---------|
| Supplier Order | Incoming from purchase. |
| Client Order | Outgoing from sale order (delivery). |
| Site Consumption | Outbound created from a consumption line. |
| Internal Transfer | Internal transfer (e.g. to site depot). |
| Return to Supplier | Return from receipt. |
| Loss / Waste | Scrap/loss. |

---

## 11. Acceptance Scenarios (End-to-End)

Use the mock data above (customer Demo Building Corp, site Tour La Défense – Flocking, products Fireproof mortar / Mineral wool 100mm / Fixing paste, location Site 202501001 depot).

### S1 — Automatic reservation

1. Ensure **Fireproof mortar** on-hand ≥ 20 kg.  
2. **Quotes** → **New** → Customer = Demo Building Corp, line Fireproof mortar qty 20, unit price 15.  
3. **Confirm** → **Create site** when asked.  
4. **Stocks & Logistics → Transfers** → open the delivery → **Check Availability** → **Validate**.  
5. **Verify**: Delivery **BTP Site** = Tour La Défense – Flocking; moves **BTP Origin** = Client Order; on-hand −20 kg.

### S2 — Site consumption and overconsumption

1. **Consumptions** → **New** → Site = Tour La Défense – Flocking, Article = Fireproof mortar, **Planned** = 250, **Actual** = 300 → Save.  
2. **Verify**: **Variance** = 50, **Overconsumption Alert** = Yes; in list, filter/sort by Overconsumption Alert.

### S3 — Internal transfer to site depot

1. **Transfers** → **New** (Internal) → From = WH/Stock, To = Site 202501001 depot.  
2. Add move: Mineral wool 100mm, Demand = 10. Set **Site** and **BTP Origin** = Internal Transfer on the move → **Validate**.  
3. **Verify**: **Moves** filtered by BTP Site = Tour La Défense – Flocking: one move To = Site 202501001 depot, BTP Origin = Internal Transfer.

### S4 — Rolling inventory

1. **Inventory → Adjustments → Physical Inventory** → Location = WH/Stock, line Fireproof mortar **Counted** = 95 → **Apply**.  
2. **Verify**: Adjustment move created; Fireproof mortar on-hand = 95.

### S5 — Create outbound from consumption

1. **Consumptions** → **New** → Site = Tour La Défense – Flocking, Article = **Mineral wool 100mm** (storable), Planned = 15, Actual = 15 → Save.  
2. **Create Outbound Move** → Confirm and Validate the move.  
3. Reopen consumption: **Actual Quantity** = 15, **Stock Move** filled.

---

## 12. Troubleshooting

| Problem | What to check |
|---------|----------------|
| **Transfers / Moves / Products (Stock) menus missing** | User needs **Inventory User** (or Manager): Settings → Users → [User] → Inventory. |
| **Delivery moves have no BTP Site** | Sale order must have **BTP Site** set (e.g. created with "Create site" or set manually). |
| **Create Outbound Move not visible** | Article must be **Storable** and **Stock Move** must be empty. |
| **No warehouse** | Company must have at least one warehouse: Inventory → Configuration → Warehouses. |
| **Outbound move goes to scrap** | If no location has **Site** = consumption’s site, the move uses company **scrap** location. Create a site depot location and set **Site** on it to use it as destination. |
| **Consumable on quote** | Consumables do not create stock reservations; they only appear in Consumptions (planned/actual). Use storable products for reservations and outbound moves. |
| **RPC_ERROR / TimeoutError / ClientDisconnected** | Usually a network or proxy timeout between browser and server. Retry the action; if it persists, check VPN/proxy timeouts, server load, or try a shorter path (e.g. set Site/BTP Origin in the Operations list on the transfer instead of opening many forms). |

---

## 13. Quick Reference — Key Fields

| Model | Field | Meaning |
|-------|--------|--------|
| **stock.location** | Site (btp_site_id) | Site when location is a site depot. |
| **stock.move** | Site (btp_site_id) | Site concerned by the move. |
| **stock.move** | BTP Origin (btp_origin_type) | supplier_order / client_order / site_consumption / transfer / return / loss. |
| **stock.move** | Site Consumption (btp_consumption_id) | Consumption line when origin = site_consumption. |
| **stock.picking** | BTP Site (btp_site_id) | Computed from first move with a site. |
| **btp.site.consumption** | Stock Move (stock_move_id) | Outbound move created from this consumption. |

---

## 14. Summary Checklist

- [ ] Warehouses and locations exist; site depots have **Site** (BTP) set on the location.  
- [ ] Products used for stock are **Storable**; consumables are only in consumptions.  
- [ ] Quote/order has **BTP Site** so delivery moves get **BTP Site** and **BTP Origin** = Client Order.  
- [ ] Consumptions have **Planned** and **Actual**; for storable products use **Create Outbound Move** when you want to deduct stock.  
- [ ] Transfers and Moves show **BTP Site** / **BTP Origin** where relevant; use filters and Pivot for traceability and KPIs.
