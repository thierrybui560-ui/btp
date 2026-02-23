## BTP Prospecting (Module 6) — Planning & Yield Tracking

This guide describes how to use **Planning & Yield Tracking**: site planning from quotes, yield entries, pointing, consumptions, and reports.

---

## Table of Contents

1. [Objectives & Scope](#1-objectives--scope)
2. [Where to Find Module 6 in the UI](#2-where-to-find-module-6-in-the-ui)
3. [Prerequisites](#3-prerequisites)
4. [Site Planning (Gantt from Quote)](#4-site-planning-gantt-from-quote)
5. [Yield Tracking](#5-yield-tracking)
6. [Team and Person Pointing](#6-team-and-person-pointing)
7. [Article Consumption Tracking](#7-article-consumption-tracking)
8. [Reports & KPIs](#8-reports--kpis)
9. [Yield Alert Threshold (Optional Config)](#9-yield-alert-threshold-optional-config)
10. [Acceptance Scenarios S1–S5](#10-acceptance-scenarios-s1s5)
11. [Troubleshooting](#11-troubleshooting)

---

## 1) Objectives & Scope

- **Plan and track** site execution in time (planning) and productivity (yields).
- **Pointing**: teams and subcontractors linked to site and tasks (hours, quantities).
- **Consumption**: actual article consumption vs quote forecasts, with variance and alerts.
- **Reports**: yield by day/task/site, consumption by article/site, pointing by site/person.

---

## 2) Where to Find Module 6 in the UI

Navigation:

- **BTP Prospecting → Sites & Documents → Sites**  
  Open a site → **Planning** tab: generate planning from quote, view tasks (Gantt/list).
- **BTP Prospecting → Sites & Documents → Planning & Yield → Yield Entries**
- **BTP Prospecting → Sites & Documents → Planning & Yield → Pointing**
- **BTP Prospecting → Sites & Documents → Planning & Yield → Consumptions**

If menus are not visible, ensure your user has **BTP Salesperson**, **BTP Manager**, or **BTP Administrator**.

---

## 3) Prerequisites

- A **Site** created (e.g. from an accepted quote — Module 5).
- The site has a **Sale Order** linked (`btp_sale_order_id`) so that “Generate planning from quote” is available.
- Quote has **Lots → Titles → Subtitles → Items** (Module 3).

---

## 4) Site Planning (Gantt from Quote)

**Goal:** Turn quote items into planning tasks and open them in a list or Gantt/Calendar view so you can see the timeline, edit dates/assignees, and then record Yield, Pointing, and Consumptions.

### Steps

1. Go to **Sites & Documents → Sites** and open a site that has a linked **Sale Order** (field **Source Quote/Order**).
2. Open the **Planning** tab.
3. If the site has no planning tasks yet, click **Generate planning from quote**.
4. Tasks are created from **each quote item** in the order: **Lot → Title → Subtitle → Item**, with:
   - **Name** = quote item name  
   - **Quote Item** = link to the source item  
   - **Planned quantity** and **UoM** from the quote item  
   - **Start / End** spread evenly between the site’s **Start date** and **Planned end date**
5. The action opens the **project tasks** for this site. Use the **List** view to see all tasks, or switch to **Calendar** (community) or **Gantt** (if available, e.g. Enterprise) to see and reorganize tasks on a timeline.

**Expected:**

- **One task per quote item**; all tasks are linked to the site (project).
- You can edit tasks (dates, assignees) and add **Yield**, **Pointing**, and **Consumptions** from the task form (BTP Planning group and notebook tabs).

---

### Example with mock data

**1) Quote structure (Sale Order with BTP lots)**

Assume the linked quote has this structure:

| Level    | Name / Example |
|----------|----------------|
| **Lot**  | Lot 1 – Groundworks |
| **Title** | 1.1 Earthworks |
| **Subtitle** | 1.1.1 Excavation |
| **Items** | • Item: “Excavation 0–2 m”, Qty: **150**, UoM: **m³** |
|          | • Item: “Backfill”, Qty: **80**, UoM: **m³** |
| **Subtitle** | 1.1.2 Formwork |
| **Items** | • Item: “Formwork linear”, Qty: **120**, UoM: **m** |
| **Title** | 1.2 Foundations |
| **Subtitle** | 1.2.1 Concrete |
| **Items** | • Item: “Concrete C25/30”, Qty: **25**, UoM: **m³** |

So there are **4 quote items** in order: Excavation 0–2 m, Backfill, Formwork linear, Concrete C25/30.

**2) Site dates**

- **Start date:** 2026-03-01  
- **Planned end date:** 2026-03-31  
- So the planning window is **31 days**.

**3) What “Generate planning from quote” creates**

The button creates **one project task per quote item**, in the same order (Lot → Title → Subtitle → Item). Dates are spread evenly over the 31 days:

| # | Task name            | Quote item        | Planned qty | UoM | Start     | End       |
|---|----------------------|-------------------|-------------|-----|-----------|-----------|
| 1 | Excavation 0–2 m     | (link to item 1)  | 150         | m³  | 01/03/26  | 08/03/26  |
| 2 | Backfill             | (link to item 2)  | 80          | m³  | 08/03/26  | 16/03/26  |
| 3 | Formwork linear      | (link to item 3)  | 120         | m   | 16/03/26  | 24/03/26  |
| 4 | Concrete C25/30     | (link to item 4)  | 25          | m³  | 24/03/26  | 31/03/26  |

- **Start/End:** The algorithm splits the period (Start date → Planned end date) into as many segments as there are *new* items and assigns each task a segment (task 1: first segment, task 2: second, etc.).
- **Planned quantity & UoM** are copied from the quote item.
- **Quote Item** on each task links back to the BTP quote item (used for Yield and Consumptions).

**4) What you do next**

- **List view:** You see the 4 tasks with columns such as Task, Quote Item, Planned quantity, UoM, Start/End (or Deadline). You can edit dates and assignees.
- **Calendar / Gantt:** Switch view to see tasks on a timeline and drag to reschedule if needed.
- **Task form:** Open any task to:
  - **Yield** tab: record expected vs actual quantity per day (only if the task has a Quote Item).
  - **Pointing** tab: record who worked (employee or subcontractor), hours, quantity done.
  - **Consumptions** tab: record actual article consumption vs quote (only if the task has a Quote Item).

**5) If you click “Generate planning from quote” again**

- Only **new** quote items get a task. Items that already have a task for this site are skipped.
- If all items already have tasks, you get a message like: *“Planning already generated for all quote items. Delete existing planning tasks if you want to regenerate.”*

---

## 5) Yield Tracking

Goal: Record expected vs actual quantity per day and get yield rate and alerts.

Steps:

1. Open a **Site** → **Planning** tab → open a **Task** (or go to **Planning & Yield → Yield Entries** and create/new).
2. In the task form, open the **Yield** tab (visible when the task has a **Quote Item**).
3. Click **Add a line** and set:
   - **Date**, **Expected Qty**, **Actual Qty**, **Unit**
4. Save.

The system computes:

- **Yield Rate %** = (Actual / Expected) × 100.
- **Yield alert**: when the rate is below the configured threshold (default 80%), the line is flagged.

You can also create yield entries from **Planning & Yield → Yield Entries** and group by Task or Site.

---

## 6) Team and Person Pointing

Goal: Record who worked on which site/task (employee or subcontractor), hours and quantity.

Steps:

1. From a **Task** form, open the **Pointing** tab, or go to **Planning & Yield → Pointing**.
2. Create a line with:
   - **Site**, **Task**, **Date**
   - **Employee** *or* **Subcontractor** (exactly one required)
   - **Hours**, **Quantity done**, **Unit**

Each line is attached to the site, the task, and the employee/subcontractor. From an employee or subcontractor file you can see their interventions (via the pointing model linked to site/task).

---

## 7) Article Consumption Tracking

Goal: Compare actual consumption to quote (planned) and get variance and overconsumption alerts.

Steps:

1. From a **Task** form, open the **Consumptions** tab (visible when the task has a Quote Item), or go to **Planning & Yield → Consumptions**.
2. Create a line:
   - **Site**, **Task**, **Quote Item**, **Article** (product)
   - **Planned quantity** (from quote), **Actual quantity**
3. Save.

The system computes:

- **Variance** = Actual − Planned.
- **Overconsumption alert**: set when planned > 0 and variance > 0.

---

## 8) Reports & KPIs

- **Yield Entries**  
  Use **Pivot** and **Graph** views (by Site, Task, Date) to analyse expected vs actual and yield rate.
- **Pointing**  
  Use **Pivot** (by Site, Date) to see hours and quantity by site/person.
- **Consumptions**  
  Use **Pivot** (by Site, Article) to see planned vs actual and variance.

Filters:

- Yield: filter **Yield alert** to see only under-threshold entries.
- Consumption: filter **Overconsumption** to see only overconsumption alerts.

---

## 9) Yield Alert Threshold (Optional Config)

The yield alert is triggered when **Yield Rate %** is below a threshold. Default: **80%**.

To change it (technical):

- System parameter: `btp_prospecting.btp_yield_alert_threshold` (e.g. `80` for 80%).
- Set via **Settings → Technical → Parameters → System Parameters**, or programmatically.

---

## 10) Acceptance Scenarios S1–S5

**S1 — Automatic Gantt**  
Accept a quote → site is created → open site → **Planning** tab → **Generate planning from quote** → tasks appear; open in Gantt/list. ✓

**S2 — Yield entry**  
On a task, add a Yield line: Expected 100 m², Actual 80 m² → Yield rate 80%. If threshold is 80%, alert may appear depending on configuration. ✓

**S3 — Employee pointing**  
Create a Pointing line: Site Y, Task, Date 02/09, Employee X, hours and qty. Entry is attached to site + task + employee. ✓

**S4 — Article overconsumption**  
Create a Consumption line: planned 500 kg, actual 650 kg → variance +150 kg, overconsumption alert. ✓

**S5 — Management report**  
Use Pivot on Yield (by task/site), Pointing (by site/date), Consumption (by site/article) for planned vs actual and deviations. ✓

---

## 11) Troubleshooting

**“Generate planning from quote” is hidden**  
The site must have a **Sale Order** linked. If you already generated planning once, the button is hidden to avoid duplicating tasks.

**Yield tab not visible on task**  
The Yield tab is shown when the task has a **Quote Item**. Set **Quote Item** in the BTP Planning group on the task.

**Pointing: “Please set either Employee or Subcontractor”**  
Each pointing line must have exactly one of **Employee** or **Subcontractor** (not both, not none).

**Consumption variance / overconsumption**  
Variance = Actual − Planned. Overconsumption alert is when planned > 0 and variance > 0.

**Menus “Planning & Yield” not visible**  
Check that the user has at least **BTP Salesperson** (or Manager/Administrator) and refresh the menu after group changes.
