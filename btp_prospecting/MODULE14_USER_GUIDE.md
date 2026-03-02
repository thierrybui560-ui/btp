# Module 14 — Mobile Application (Android & iOS) — User & Implementation Guide

This guide describes **Module 14**: mobile access to BTP Prospecting via **PWA (Progressive Web App)** and a **JSON API** for custom mobile clients. It is based on Odoo 19 and the current BTP implementation.

---

## 1. Objectives & Scope (Summary)


| Goal                  | What the system provides                                                                                                                   |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Mobile access**     | Use Odoo from the field via PWA (browser “Add to home screen”) or a custom app calling the BTP Mobile API.                                 |
| **Commercial**        | Create leads (with optional photo), view clients/contacts, list and open quotes, get quote PDF.                                            |
| **Sites**             | List active sites, view site documents, submit pointing (team/subcontractor), submit daily yields.                                         |
| **QHSE**              | Declare incidents with description and optional photo.                                                                                     |
| **Tasks & reminders** | List current user’s activities; dashboard KPIs; notifications/reminders (quote follow-up, overdue tasks).                                  |
| **Push / alerts**     | Alerts are exposed via the **notifications** API (polling). True push (FCM/APNs) requires a separate push service and optional native app. |
| **Offline**           | Full offline with sync is not implemented in-core; the API supports future native apps that implement local storage and sync.              |


---

## 2. Recommended Approach: PWA + Mobile API

- **PWA (Odoo 19 recommended)**  
  - Use the standard Odoo web interface in a mobile browser and **install the PWA** (e.g. Chrome “Install app” / Safari “Add to Home Screen”).  
  - Same login as web; access to all BTP menus (Leads, Clients, Quotes, Sites, Pointing, QHSE, etc.) with existing rights.  
  - No separate app store deployment; works on Android and iOS (iOS 16.4+ for full PWA features).
- **Mobile API (JSON)**  
  - Module 14 adds a **BTP Mobile API** (`/btp/mobile/...`) for:  
    - Leads (list, create with optional photo)  
    - Partners (clients/contacts)  
    - Quotes (list, get, PDF URL)  
    - Sites (list, site documents)  
    - Pointing and yield creation  
    - QHSE incident creation (with optional photo)  
    - Tasks (activities), dashboard KPIs, notifications
  - Use this API from:  
    - A **custom native/hybrid app** (e.g. React Native, Flutter) for offline-capable UIs and future push.  
    - **PWA or any client** that needs structured data (e.g. custom mobile dashboard).
- **Offline & push**  
  - **Offline**: Not implemented in the Odoo addon. A custom app can cache API responses and implement sync when back online.  
  - **Push**: The **notifications** endpoint returns “alerts” (overdue tasks, quote reminders). To send real push to devices (FCM/APNs), add an external push service and optionally a small backend that calls this API and forwards to FCM/APNs.

---

## 3. API Endpoints (Module 14)

All routes are **JSON** (`type='json'`), **auth='user'** (session login). Base URL: same as your Odoo instance (e.g. `https://your-odoo.com`). Call via Odoo’s JSON-RPC or HTTP POST with JSON body and session cookie.


| Method / Route                              | Purpose                                                                                                                                                                                                                                    |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `POST /btp/mobile/leads`                    | List leads (assigned or common open). Params: `limit`, `offset`.                                                                                                                                                                           |
| `POST /btp/mobile/lead/create`              | Create lead from field. Params: `name`, `site_name`, `site_address`, `site_city`, `site_zip`, `site_country_id`, `site_type`, `partner_name`, `partner_email`, `partner_phone`, `description`, `origin_detail`, `photo_base64` (optional). |
| `POST /btp/mobile/partners`                 | List clients/contacts. Params: `limit`, `offset`, `search`.                                                                                                                                                                                |
| `POST /btp/mobile/quotes`                   | List quotes. Params: `limit`, `offset`, `state` (optional).                                                                                                                                                                                |
| `POST /btp/mobile/quote/<order_id>`         | Get one quote and PDF URL.                                                                                                                                                                                                                 |
| `POST /btp/mobile/sites`                    | List BTP sites. Params: `limit`, `offset`, `active_only`.                                                                                                                                                                                  |
| `POST /btp/mobile/site/<site_id>/documents` | List site documents.                                                                                                                                                                                                                       |
| `POST /btp/mobile/pointing/create`          | Submit pointing. Params: `site_id`, `date`, `user_id`, `subcontractor_id`, `hours`, `qty_done`, `notes`.                                                                                                                                   |
| `POST /btp/mobile/yield/create`             | Submit yield. Params: `task_id`, `date`, `expected_qty`, `real_qty`, `notes`.                                                                                                                                                              |
| `POST /btp/mobile/incident/create`          | Create QHSE incident. Params: `site_id`, `description`, `incident_type`, `location`, `photo_base64` (optional).                                                                                                                            |
| `POST /btp/mobile/tasks`                    | List current user’s activities. Params: `limit`.                                                                                                                                                                                           |
| `POST /btp/mobile/dashboard`                | Dashboard KPIs: leads_count, leads_converted_this_month, quotes_pending, sites_active, activities_count.                                                                                                                                   |
| `POST /btp/mobile/notifications`            | Alerts: overdue tasks, quote reminders. Params: `limit`.                                                                                                                                                                                   |


Response format: `{ "success": true, "data": ... }` or `{ "success": false, "error": "..." }`.

---

## 4. PWA: How to Use on Mobile

1. On the mobile device, open your Odoo URL in a supported browser (Chrome, Safari, Edge, etc.).
2. Log in (same user as web).
3. Install the PWA:
  - **Android (Chrome)**: Menu → “Install app” / “Add to Home screen”.  
  - **iOS (Safari 16.4+)**: Share → “Add to Home Screen”.
4. Open the app from the home screen; use BTP menus (Leads, Clients & Contacts, Quotes & Articles, Sites & Documents, etc.) as on desktop.
5. For **quote PDF**: open the quote in the PWA and use Print / Share to PDF, or call the Mobile API `quote/<id>` to get `pdf_url` and open it in the browser.

---

## 5. Acceptance Scenarios (Mapping)


| Scenario                      | How it is covered                                                                                                                                                                                                                                                                                                                    |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **S1 — Field lead creation**  | PWA: create lead from Leads → New. API: `POST /btp/mobile/lead/create` with name, site, partner, optional `photo_base64`. Lead is created and can be auto-assigned (existing BTP rules).                                                                                                                                             |
| **S2 — Mobile pointing**      | PWA: Sites → open site → Pointing (or equivalent). API: `POST /btp/mobile/pointing/create` with `site_id`, `user_id` or `subcontractor_id`, `hours`/`qty_done`, `date`. Data is stored on the server and linked to the site. QR code scanning can be implemented in a custom app that then calls this API with the resolved site_id. |
| **S3 — Offline incident**     | Not in-core. A custom app can store the payload locally and, when online, call `POST /btp/mobile/incident/create` (with optional `photo_base64`).                                                                                                                                                                                    |
| **S4 — Delay notification**   | `POST /btp/mobile/notifications` returns alerts (e.g. quote reminders, overdue tasks). A custom app or PWA can poll this and show in-app alerts; for push to device, add FCM/APNs and a small backend that consumes this API.                                                                                                        |
| **S5 — Quote PDF in meeting** | PWA: open quote → print/share as PDF. API: `POST /btp/mobile/quote/<id>` returns `pdf_url`; open in browser or in-app webview.                                                                                                                                                                                                       |


---

## 6. Security & Access

- All mobile routes require **authenticated user** (`auth='user'`). Use the same login as web (and 2FA if configured in Odoo).  
- Data is filtered by **existing BTP rights** (record rules, groups: salesperson, manager, admin). No extra mobile-specific permissions.  
- For “lost device”: use Odoo’s **Change password** and, if available, **terminate sessions**; the API does not store device tokens. A custom app can implement local data wipe on logout.

---

## 7. Key Files (Implementation)


| File                                                               | Role                                                                                                              |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `odoo19/addons/btp_prospecting/controllers/btp_mobile_api.py`      | Module 14 JSON API (leads, partners, quotes, sites, pointing, yield, incidents, tasks, dashboard, notifications). |
| `odoo19/addons/btp_prospecting/controllers/btp_lead_controller.py` | Existing web form and `/btp/lead/mobile` (legacy); Module 14 uses `/btp/mobile/lead/create` with photo support.   |
| `controllers/__init__.py`                                          | Imports `btp_mobile_api`.                                                                                         |


---

## 8. Optional: Custom Native App

To build a dedicated Android/iOS app with offline and push:

1. Use the **BTP Mobile API** above for all data (leads, sites, quotes, pointing, yields, incidents, tasks, dashboard, notifications).
2. Authenticate via Odoo’s **JSON-RPC** (e.g. `/web/session/authenticate`) and keep session cookie or token.
3. Implement **local storage** (e.g. SQLite) and a **sync layer** that writes to the API when online; resolve conflicts (e.g. “priority to server” as per spec) in your app.
4. Implement **push**: backend job that calls `/btp/mobile/notifications` (or equivalent) and sends payloads to **FCM** (Android) / **APNs** (iOS); store device tokens in your backend, not in Odoo core.
5. **Scanner**: use device camera + barcode/QR library; decode site or article ID and call the relevant API (e.g. pointing with `site_id`).

---

## 9. Summary Checklist

- **PWA**: Install Odoo as PWA on the phone; use BTP as on desktop (Leads, Clients, Quotes, Sites, Pointing, QHSE, etc.).  
- **Mobile API**: Use `/btp/mobile/`* for list/create/get and PDF URL; same rights as web.  
- **Leads**: Create via PWA or `lead/create` (optional photo).  
- **Pointing / Yield**: Submit via API or PWA.  
- **QHSE**: Declare incident via PWA or `incident/create` (optional photo).  
- **Alerts**: Poll `notifications`; add FCM/APNs for real push if needed.  
- **Offline**: Implement in a custom app with local cache and sync to this API.

