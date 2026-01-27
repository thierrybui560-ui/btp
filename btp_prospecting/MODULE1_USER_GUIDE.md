## BTP Prospecting (Module 1) - Complete User Guide

This comprehensive guide provides detailed step-by-step instructions with complete mock data for every use case in the BTP Prospecting module.

---

## Table of Contents

1. [Finding the Module](#1-where-to-find-the-module-in-the-ui)
2. [Initial Setup - Complete Scenarios](#2-initial-setup-complete-scenarios)
3. [Company Setup - Multi-Company Scenarios](#3-company-setup-multi-company-scenarios)
4. [Lead Stages - Workflow Setup](#4-lead-stages-workflow-setup)
5. [Assignment Rules - Complete Scenarios](#5-assignment-rules-complete-scenarios)
6. [Creating Leads - All Scenarios with Complete Mock Data](#6-creating-leads-all-scenarios-with-complete-mock-data)
7. [Taking Open Leads - Scenarios](#7-taking-open-leads-scenarios)
8. [Assigning Leads - Scenarios](#8-assigning-leads-scenarios)
9. [Setting Reminders - Scenarios](#9-setting-reminders-scenarios)
10. [Duplicate Detection and Merging - Scenarios](#10-duplicate-detection-and-merging-scenarios)
11. [Converting Leads to Opportunities](#11-converting-leads-to-opportunities)
12. [Multi-Company Sharing - Scenarios](#12-multi-company-sharing-scenarios)
13. [Reminder System Testing - Complete Guide](#13-reminder-system-testing-complete-guide)
14. [Escalation System - Scenarios](#14-escalation-system-scenarios)
15. [Round-Robin Assignment Testing](#15-round-robin-assignment-testing)
16. [Pyramidal Visibility Testing](#16-pyramidal-visibility-testing)
17. [Open Leads Queue - Detailed Scenarios](#17-open-leads-queue-detailed-scenarios)
18. [Reports](#18-reports)
19. [Spec Alignment](#19-spec-alignment-what-exists-vs-what-is-not-yet)
20. [Quick Mock Dataset](#20-quick-mock-dataset-copypaste)
21. [Troubleshooting](#21-troubleshooting)
22. [What This Module Does Not Include Yet](#22-what-this-module-does-not-include-yet)

---

## 1) Where to find the module in the UI

### Step-by-Step Instructions:

1. **Open Odoo** in your browser (typically `http://localhost:8069`)
2. **Login** with your user credentials
3. **Click the 9-dot App Switcher** (top-left corner, next to the Odoo logo)
4. **Scroll or search** for "BTP Prospecting"
5. **Click on "BTP Prospecting"**

### Expected Menu Structure:

After clicking, you will see in the top navigation bar:
- **BTP Prospecting** (main menu)
  - **Leads** (shows all leads, default view)
  - **All Leads** (same as Leads, alternative entry point)
  - **Open Leads** (shows only common open leads)
  - **Configuration** (dropdown)
    - **Lead Stages**
    - **Assignment Rules**

### If Module is Not Visible:

**Problem**: "BTP Prospecting" does not appear in the app switcher

**Solution Steps**:
1. Go to **Apps** (from app switcher or Settings)
2. Click **Installed** filter (top-left)
3. Search for "BTP Prospecting"
4. If not found, click **Update Apps List** (top-right)
5. Search again and verify it shows as **Installed**
6. If still not visible, check your user has one of these groups:
   - **BTP Administrator**
   - **BTP Manager**
   - **BTP Salesperson**
   - **BTP Non-Sales**
7. **Log out and log back in** to refresh menu permissions

---

## 2) Initial Setup - Complete Scenarios

### 2.1 Enable Developer Mode (Required for User Groups)

**Why**: User groups (BTP Salesperson, BTP Manager, etc.) are only visible in Developer Mode.

**Steps**:
1. Login as **Administrator** (or any user with Settings access)
2. Click **Settings** (gear icon, top-right, or from app switcher)
3. Scroll to the very bottom of the Settings page
4. Find the section **"Developer Tools"**
5. Click **"Activate Developer Mode"** button
6. A confirmation dialog appears - click **"Activate"**
7. Page reloads - you should see additional menu items and options

**Verification**: After activation, you should see:
- **Technical** menu in Settings
- **Groups** menu under Users & Companies
- Additional debug options in various forms

---

### 2.2 Create Mock Users - Complete Scenario

**Scenario**: Create 5 users representing different roles for testing all module features.

#### User 1: Alice Martin (Salesperson - Paris Specialist)

**Navigation**: Settings → Users & Companies → Users → Create

**Form Fields to Fill**:
- **Name**: `Alice Martin`
- **Login**: `alice`
- **Email**: `alice@btp.local`
- **Company**: `BTP France` (select from dropdown, create if needed)
- **Language**: `English` (or your preferred language)
- **Timezone**: `Europe/Paris`

**Access Rights Tab**:
- Click **"Access Rights"** tab
- Find **"BTP Prospecting"** section
- Check **"BTP Salesperson"** checkbox
- (Do NOT check BTP Manager or BTP Administrator)

**Preferences Tab** (Optional):
- **Notification**: `Handle by Emails`
- **Email Signature**: `Alice Martin - BTP Sales`

**Save**: Click **"Save"** button (top-left)

**Expected Result**: User created successfully, you see "Alice Martin" in the users list.

---

#### User 2: Bernard Leroy (Salesperson - General)

**Navigation**: Settings → Users & Companies → Users → Create

**Form Fields**:
- **Name**: `Bernard Leroy`
- **Login**: `bernard`
- **Email**: `bernard@btp.local`
- **Company**: `BTP France`
- **Language**: `English`
- **Timezone**: `Europe/Paris`

**Access Rights Tab**:
- Check **"BTP Salesperson"**

**Save**: Click **"Save"**

---

#### User 3: Chloe Durand (Non-Sales - Lead Entry)

**Navigation**: Settings → Users & Companies → Users → Create

**Form Fields**:
- **Name**: `Chloe Durand`
- **Login**: `chloe`
- **Email**: `chloe@btp.local`
- **Company**: `BTP France`
- **Language**: `English`
- **Timezone**: `Europe/Paris`

**Access Rights Tab**:
- Check **"BTP Non-Sales"** (NOT BTP Salesperson)

**Save**: Click **"Save"**

**Note**: Non-Sales users can create leads but they are automatically set as "Common Open" and not auto-assigned.

---

#### User 4: David Roche (Manager - Supervisor)

**Navigation**: Settings → Users & Companies → Users → Create

**Form Fields**:
- **Name**: `David Roche`
- **Login**: `david`
- **Email**: `david@btp.local`
- **Company**: `BTP France`
- **Language**: `English`
- **Timezone**: `Europe/Paris`

**Access Rights Tab**:
- Check **"BTP Manager"**

**Save**: Click **"Save"**

**Note**: Managers can see all leads from their subordinates (pyramidal hierarchy).

---

#### User 5: Emma Petit (Salesperson - Belgium)

**Navigation**: Settings → Users & Companies → Users → Create

**Form Fields**:
- **Name**: `Emma Petit`
- **Login**: `emma`
- **Email**: `emma@btp.local`
- **Company**: `BTP Belgium` (different company for multi-company testing)
- **Language**: `English`
- **Timezone**: `Europe/Brussels`

**Access Rights Tab**:
- Check **"BTP Salesperson"**

**Save**: Click **"Save"**

---

### 2.3 Set Manager Hierarchy (Pyramidal Visibility)

**Purpose**: Configure so David (Manager) can see Alice and Bernard's leads, but Alice and Bernard cannot see each other's leads.

#### Step 1: Set Alice's Manager

**Navigation**: Settings → Users & Companies → Users

**Steps**:
1. Find and click **"Alice Martin"** in the list
2. Click **"Edit"** (or double-click to open)
3. Go to **"Preferences"** tab (or scroll down if all fields are on one page)
4. Find field **"Manager"** (under BTP Prospecting section)
5. Click the dropdown and select **"David Roche"**
6. Click **"Save"**

**Expected Result**: Alice's form shows Manager = David Roche

---

#### Step 2: Set Bernard's Manager

**Navigation**: Settings → Users & Companies → Users

**Steps**:
1. Find and click **"Bernard Leroy"**
2. Click **"Edit"**
3. Go to **"Preferences"** tab
4. Set **"Manager"** = **"David Roche"**
5. Click **"Save"**

**Expected Result**: Bernard's form shows Manager = David Roche

---

#### Step 3: Verify Pyramidal Visibility

**Test Scenario**:
1. **Login as Alice** (`alice` / password)
2. Create a lead (see Section 6 for details)
3. **Logout**
4. **Login as Bernard** (`bernard` / password)
5. Go to **BTP Prospecting → Leads**
6. **Expected**: Bernard should NOT see Alice's lead
7. **Logout**
8. **Login as David** (`david` / password)
9. Go to **BTP Prospecting → Leads**
10. **Expected**: David SHOULD see both Alice's and Bernard's leads

---

### 2.4 Round-Robin Settings (For Auto-Assignment)

**Purpose**: Configure weights for round-robin assignment. Higher weight = more leads assigned.

#### Configure Alice (Weight = 2)

**Navigation**: Settings → Users & Companies → Users

**Steps**:
1. Open **"Alice Martin"**
2. Go to **"Preferences"** tab
3. Find **"BTP Round-Robin Weight"** field
4. Enter: `2`
5. Click **"Save"**

**Meaning**: Alice will receive 2x more leads than users with weight=1 in round-robin distribution.

---

#### Configure Bernard (Weight = 1)

**Steps**:
1. Open **"Bernard Leroy"**
2. Go to **"Preferences"** tab
3. Set **"BTP Round-Robin Weight"** = `1`
4. Click **"Save"**

---

#### Configure Emma (Weight = 1)

**Steps**:
1. Open **"Emma Petit"**
2. Go to **"Preferences"** tab
3. Set **"BTP Round-Robin Weight"** = `1`
4. Click **"Save"**

---

#### Optional: Set User as Unavailable

**Scenario**: User is on vacation and should not receive new leads.

**Steps** (for example, Alice):
1. Open **"Alice Martin"**
2. Go to **"Preferences"** tab
3. Check **"BTP Unavailable"** checkbox
4. Click **"Save"**

**Result**: Alice will be excluded from round-robin assignment until unchecked.

---

#### Optional: Set User as Overloaded

**Scenario**: User has too many leads and should receive fewer new assignments.

**Steps** (for example, Bernard):
1. Open **"Bernard Leroy"**
2. Go to **"Preferences"** tab
3. Check **"BTP Overloaded"** checkbox
4. Click **"Save"**

**Result**: Bernard will receive fewer leads in round-robin (reduced weight in pool calculation).

---

### 2.5 Verify User Setup

**Checklist**:
- [ ] All 5 users created
- [ ] Each user has correct group assigned
- [ ] Alice and Bernard have David as Manager
- [ ] Round-robin weights configured
- [ ] All users can login successfully
- [ ] Each user sees "BTP Prospecting" menu after login

---

## 3) Company Setup - Multi-Company Scenarios

### 3.1 Create Companies

**Purpose**: Set up multi-company structure for testing company-based lead visibility and sharing.

#### Create BTP France Company

**Navigation**: Settings → Companies → Create

**Form Fields**:
- **Company Name**: `BTP France`
- **Email**: `contact@btp-france.fr`
- **Phone**: `+33 1 23 45 67 89`
- **Website**: `https://www.btp-france.fr`
- **Address**:
  - **Street**: `123 Avenue des Champs-Élysées`
  - **City**: `Paris`
  - **ZIP**: `75008`
  - **Country**: `France`
- **Currency**: `EUR` (Euro)
- **Fiscal Year**: `Calendar Year`

**Save**: Click **"Save"**

**Expected Result**: Company "BTP France" appears in companies list.

---

#### Create BTP Belgium Company

**Navigation**: Settings → Companies → Create

**Form Fields**:
- **Company Name**: `BTP Belgium`
- **Email**: `contact@btp-belgium.be`
- **Phone**: `+32 2 123 45 67`
- **Website**: `https://www.btp-belgium.be`
- **Address**:
  - **Street**: `456 Rue de la Loi`
  - **City**: `Brussels`
  - **ZIP**: `1000`
  - **Country**: `Belgium`
- **Currency**: `EUR` (Euro)
- **Fiscal Year**: `Calendar Year`

**Save**: Click **"Save"**

---

### 3.2 Assign Users to Companies

**Note**: This should already be done when creating users (Section 2.2), but verify:

#### Verify User-Company Assignment

**Navigation**: Settings → Users & Companies → Users

**For each user, verify**:
1. **Alice Martin**: Company = `BTP France`
2. **Bernard Leroy**: Company = `BTP France`
3. **Chloe Durand**: Company = `BTP France`
4. **David Roche**: Company = `BTP France`
5. **Emma Petit**: Company = `BTP Belgium`

**To change a user's company**:
1. Open the user form
2. Find **"Company"** field (usually in the main form or "Preferences" tab)
3. Select the correct company from dropdown
4. Click **"Save"**

---

### 3.3 Test Multi-Company Visibility

**Scenario**: Verify that users only see leads from their company (unless shared).

**Steps**:
1. **Login as Alice** (BTP France)
2. Create a lead with Company = `BTP France` (see Section 6)
3. **Logout**
4. **Login as Emma** (BTP Belgium)
5. Go to **BTP Prospecting → Leads**
6. **Expected**: Emma should NOT see Alice's lead (different companies)
7. **Logout**
8. **Login as Administrator** (or BTP Administrator)
9. Go to **BTP Prospecting → Leads**
10. **Expected**: Administrator should see leads from ALL companies

**Note**: For shared leads, see Section 12 (Multi-Company Sharing).

---

## 4) Lead Stages - Workflow Setup

### 4.1 View Default Stages

**Navigation**: BTP Prospecting → Configuration → Lead Stages

**Default Pipeline** (should already exist):
1. **New** - Initial stage for new leads
2. **Qualified** - Lead has been qualified
3. **Contacted** - Initial contact made
4. **To Remind** - Needs follow-up reminder
5. **Decision** - Client is making decision
6. **Won** - Lead converted to sale
7. **Lost** - Lead lost to competitor or client declined

**View Details**: Click on any stage to see/edit its properties.

---

### 4.2 Configure Stage Properties

**Scenario**: Configure "Qualified" stage to require reminders.

**Steps**:
1. Go to **BTP Prospecting → Configuration → Lead Stages**
2. Click on **"Qualified"** stage
3. In the form, find **"Require Reminder"** checkbox
4. **Check** the checkbox
5. Click **"Save"**

**Result**: When a lead moves to "Qualified" stage, user MUST set a "Next Reminder Date" or they cannot save.

---

### 4.3 Stage Properties Explained

**Fields in Stage Form**:
- **Name**: Stage display name (e.g., "New", "Qualified")
- **Sequence**: Order in pipeline (lower number = earlier in pipeline)
- **Qualification Status**: 
  - `Field` - Initial discovery
  - `Targeting` - Qualified and targeted
  - `Contact` - Contact made
  - `Decision` - Client deciding
- **Require Reminder**: If checked, "Next Reminder Date" is mandatory at this stage
- **Is Won**: Check if this is a "won" stage (e.g., "Won")
- **Is Lost**: Check if this is a "lost" stage (e.g., "Lost")

**Example Configuration**:
- **New**: Qualification Status = `Field`, Require Reminder = `No`
- **Qualified**: Qualification Status = `Targeting`, Require Reminder = `Yes`
- **Contacted**: Qualification Status = `Contact`, Require Reminder = `Yes`
- **To Remind**: Qualification Status = `Contact`, Require Reminder = `Yes`
- **Decision**: Qualification Status = `Decision`, Require Reminder = `Yes`
- **Won**: Qualification Status = `Decision`, Is Won = `Yes`, Require Reminder = `No`
- **Lost**: Qualification Status = `Decision`, Is Lost = `Yes`, Require Reminder = `No`

---

## 5) Assignment Rules - Complete Scenarios

### 5.1 Rule Type: Geography-Based Assignment

**Scenario**: Assign all leads from Paris and Versailles to Alice automatically.

**Navigation**: BTP Prospecting → Configuration → Assignment Rules → Create

**Form Fields**:
- **Name**: `Paris Leads -> Alice`
- **Active**: ✅ (checked)
- **Priority**: `1` (lower number = higher priority, checked first)
- **Assignment Type**: Select `Geography` from dropdown
- **Countries**: 
  - Click **"Add a line"** button
  - Select `France` from dropdown
- **City Names**: 
  - Click in the text area
  - Enter (one per line):
    ```
    Paris
    Versailles
    ```
- **Assign To**: Select `Alice Martin` from dropdown
- **Sales Team**: Leave empty (not needed for Geography type)

**Save**: Click **"Save"**

**Expected Result**: Rule appears in list with Priority = 1.

**Test This Rule**:
1. Create a new lead with:
   - City = `Paris`
   - Country = `France`
2. Save the lead
3. **Expected**: Lead is automatically assigned to Alice Martin

---

### 5.2 Rule Type: Round-Robin Assignment

**Scenario**: Distribute all other leads evenly among sales team members using round-robin.

**Navigation**: BTP Prospecting → Configuration → Assignment Rules → Create

**Form Fields**:
- **Name**: `General Round Robin`
- **Active**: ✅ (checked)
- **Priority**: `10` (lower priority than Geography rule)
- **Assignment Type**: Select `Round Robin` from dropdown
- **Sales Team**: 
  - If you have a sales team "BTP Sales", select it
  - If not, leave empty (system will use all BTP Salesperson users)
- **Assign To**: Select `David Roche` (fallback if no team members available)
- **Countries**: Leave empty
- **City Names**: Leave empty

**Save**: Click **"Save"**

**Expected Result**: Rule appears in list with Priority = 10.

**How Round-Robin Works**:
- First lead → Alice (weight=2, so counted twice)
- Second lead → Alice (weight=2)
- Third lead → Bernard (weight=1)
- Fourth lead → Emma (weight=1)
- Fifth lead → Alice (weight=2)
- And so on...

**Test This Rule**:
1. Create a lead with:
   - City = `Lyon` (not Paris or Versailles)
   - Country = `France`
2. Save the lead
3. **Expected**: Lead assigned to first available salesperson in round-robin pool (considering weights and availability)

---

### 5.3 Rule Type: Client Type Assignment

**Scenario**: Assign leads from specific client categories to specific users.

**Prerequisites**: 
- Create partner categories in Contacts → Configuration → Partner Categories
- Example categories: "Public Sector", "Private Sector", "International"

**Navigation**: BTP Prospecting → Configuration → Assignment Rules → Create

**Form Fields**:
- **Name**: `Public Sector -> David`
- **Active**: ✅
- **Priority**: `5`
- **Assignment Type**: Select `Client Type` from dropdown
- **Client Categories**: 
  - Click **"Add a line"**
  - Select `Public Sector` category
- **Assign To**: Select `David Roche`
- **Sales Team**: Leave empty

**Save**: Click **"Save"**

**Test**: Create a lead with a partner that has "Public Sector" category → should assign to David.

---

### 5.4 Rule Type: Site Type Assignment

**Scenario**: Assign leads based on site type (e.g., all "Infrastructure" leads to Emma).

**Navigation**: BTP Prospecting → Configuration → Assignment Rules → Create

**Form Fields**:
- **Name**: `Infrastructure -> Emma`
- **Active**: ✅
- **Priority**: `7`
- **Assignment Type**: Select `Site Type` from dropdown
- **Site Types**: 
  - Check `Infrastructure` checkbox
- **Assign To**: Select `Emma Petit`
- **Sales Team**: Leave empty

**Save**: Click **"Save"**

**Test**: Create a lead with Site Type = `Infrastructure` → should assign to Emma.

---

### 5.5 Rule Priority Explanation

**How Rules Are Evaluated**:
1. System checks rules in **Priority order** (1 = highest, 10 = lowest)
2. First matching rule wins
3. If no rule matches, lead remains **Common Open** (unassigned)

**Example Priority Order**:
1. Priority 1: Geography (Paris → Alice)
2. Priority 5: Client Type (Public Sector → David)
3. Priority 7: Site Type (Infrastructure → Emma)
4. Priority 10: Round-Robin (default distribution)

**Test Priority**:
- Lead from Paris with Site Type = Infrastructure
- **Expected**: Assigned to Alice (Priority 1 wins over Priority 7)

---

### 5.6 Deactivate a Rule

**Scenario**: Temporarily disable a rule without deleting it.

**Steps**:
1. Go to **BTP Prospecting → Configuration → Assignment Rules**
2. Open the rule you want to disable
3. **Uncheck** the **"Active"** checkbox
4. Click **"Save"**

**Result**: Rule is ignored during assignment, but can be reactivated later.

---

## 6) Creating Leads - All Scenarios with Complete Mock Data

### 6.1 Scenario A: Salesperson Creates a Complete Lead (Auto-Assigned)

**User**: Alice Martin (BTP Salesperson)  
**Purpose**: Create a fully qualified lead that will be auto-assigned based on geography rule.

**Navigation**: BTP Prospecting → Leads → Create (or click "Create" button)

---

#### Step 1: Fill Main Form Fields

**Top Section** (visible immediately):
- **Lead Title**: `Tour Horizon - Fireproofing`
  - *Description*: Descriptive name for the lead/project
- **Site Name**: `Tour Horizon`
  - *Description*: Name of the construction site or building
- **Origin**: Select `Field Discovery` (radio button)
  - *Options*: Field Discovery, Web Form, Social Media, Partner, AI Auto-Search, File Import, Public Tender, Referral, Other
- **Origin Detail**: `On-site visit during routine inspection`
  - *Description*: Additional details about how the lead was discovered
- **Tags**: (Optional) Click "Add a line" and create tags like:
  - `Fireproofing`
  - `Commercial`
  - `High Priority`

**Right Side Fields**:
- **Assigned To**: Leave empty (will be auto-assigned)
- **Common Open**: Leave unchecked (salesperson creates private lead)
- **Stage**: `New` (default, auto-selected)
- **Qualification Status**: `Field` (default)
- **Converted**: `No` (readonly, shows if already converted)

---

#### Step 2: Site Information Tab

Click **"Site Information"** tab at the bottom.

**Left Column**:
- **Site Address**: `21 Rue de Rivoli, 75001 Paris`
  - *Full address of the construction site*
- **City**: `Paris`
  - *City name (used for geography-based assignment)*
- **ZIP Code**: `75001`
- **Country**: Select `France` from dropdown

**Right Column**:
- **Site Type**: Select `Commercial` from dropdown
  - *Options*: Residential, Commercial, Industrial, Public Works, Infrastructure, Renovation, Other
- **Project Start Date**: `2026-03-15`
  - *Expected start date of the project*
- **Project Duration**: `120`
  - *Number of days the project is expected to last*
- **Tender Deadline**: `2026-02-28`
  - *Deadline for submitting the tender (DCE - Dossier de Consultation des Entreprises)*

---

#### Step 3: Client/Prospect Tab

Click **"Client/Prospect"** tab.

**Option A: If Client Exists in Contacts**:
- **Client/Prospect**: Click dropdown and select existing partner (e.g., `Bouygues Batiment`)
- **Contact Person**: Select contact from dropdown (e.g., `Jean Dupont`)
- **Email**: Auto-filled from contact
- **Phone**: Auto-filled from contact

**Option B: If Client Does Not Exist** (use this for mock data):
- **Client Name**: `Bouygues Batiment`
  - *Name appears when "Client/Prospect" field is empty*
- **Contact Person**: Leave empty (or create contact first in Contacts app)
- **Email**: `j.dupont@bouygues.fr`
- **Phone**: `+33 6 11 22 33 44`

**Note**: You can create the partner later and link it to the lead.

---

#### Step 4: Qualification Tab

Click **"Qualification"** tab.

**Left Column**:
- **Estimated Budget**: `180000`
  - *Total project budget in EUR*
- **Probability (%)**: `40`
  - *Chance of winning this lead (0-100%)*
  - *You can type directly or use the slider*
- **Expected Revenue**: `72000` (auto-calculated: 180000 × 40%)
  - *Readonly field, computed from Budget × Probability*

**Right Column**:
- **Competitors**: 
  - Click **"Add a line"**
  - Type `Vinci` and select from dropdown (or create if needed)
  - Click **"Add a line"** again
  - Type `Eiffage` and select
  - *These should be existing partners marked as companies*
- **Response Status**: Select `Later` from dropdown
  - *Options*: Interested, Not Interested, Later, No Need Now, Lost, Won
- **Response Note**: `Client will reopen tender in March. Need to follow up.`
  - *Free text field for additional notes about client response*

---

#### Step 5: Follow-up Tab

Click **"Follow-up"** tab.

- **Next Reminder Date**: 
  - Click the datetime field
  - Select date: `Tomorrow` (or specific date like `2026-01-23 09:00:00`)
  - *This is mandatory if the current stage requires reminders*
- **Last Reminder Date**: (Readonly, shows when last reminder was sent)
- **Reminder Count**: `0` (Readonly, shows number of reminders sent)

**Escalation Fields** (Readonly, for information):
- **Escalated**: `No`
- **Escalation Date**: (empty)
- **Escalation Reason**: (empty)

---

#### Step 6: Additional Tabs (Optional)

**Description Tab**:
- **Description**: 
  ```
  Large commercial building in central Paris requiring fireproofing services.
  Building is 25 stories high. Project includes fireproofing of structural elements,
  installation of fire doors, and fire alarm system integration.
  Client is Bouygues Batiment, major construction company.
  Tender deadline is end of February 2026.
  ```

**Internal Notes Tab**:
- **Internal Notes**: 
  ```
  Initial contact made during site visit. Project manager Jean Dupont showed interest.
  Budget confirmed at 180k EUR. Competition includes Vinci and Eiffage.
  Need to prepare technical proposal by mid-February.
  ```

**Multi-Company Tab** (if multi-company enabled):
- **Company**: `BTP France` (auto-filled from user's company)
- **Sharing Type**: `Exclusive` (default, only BTP France can see)
  - *Options*: Exclusive, Shared, Global
- **Shared Companies**: (only visible if Sharing Type = Shared)

**Duplicates Tab**:
- **Is Duplicate**: Leave unchecked
- **Original Lead**: (only visible if Is Duplicate = Yes)
- **Duplicates**: (readonly list, shows potential duplicates)

---

#### Step 7: Save the Lead

Click **"Save"** button (top-left).

**Expected Results**:
1. ✅ Lead is created and saved
2. ✅ Lead is **automatically assigned to Alice Martin** (because City = Paris matches geography rule)
3. ✅ **Expected Revenue** = 72,000 EUR (180,000 × 40%)
4. ✅ Lead appears in Alice's lead list
5. ✅ Lead stage = "New"
6. ✅ Assignment Rule field shows "Paris Leads -> Alice" (readonly)

**Verify Assignment**:
- Open the lead again
- Check **"Assigned To"** field = Alice Martin
- Check **"Assignment Rule"** field (in form, may be in a separate section) = "Paris Leads -> Alice"

---

### 6.2 Scenario B: Non-Sales User Creates an Open Lead

**User**: Chloe Durand (BTP Non-Sales)  
**Purpose**: Non-sales user creates a lead that remains "Common Open" for sales team to claim.

**Navigation**: BTP Prospecting → Leads → Create

---

#### Step 1: Fill Basic Information

**Top Section**:
- **Lead Title**: `Hospital Renovation - Spraying`
- **Site Name**: `Hôpital Edouard Herriot`
- **Origin**: Select `Manual Entry`
- **Origin Detail**: `Received via phone call from hospital administration`

**Right Side**:
- **Assigned To**: Leave empty (will remain empty)
- **Common Open**: ✅ **Automatically checked** (non-sales users cannot assign leads)
- **Stage**: `New`

---

#### Step 2: Site Information Tab

- **Site Address**: `5 Place d'Arsonval, 69003 Lyon`
- **City**: `Lyon`
- **ZIP Code**: `69003`
- **Country**: `France`
- **Site Type**: `Public Works`

---

#### Step 3: Client/Prospect Tab

- **Client Name**: `Hospices Civils de Lyon`
- **Email**: `contact@chu-lyon.fr`
- **Phone**: `+33 4 72 11 69 11`

---

#### Step 4: Qualification Tab

- **Estimated Budget**: `120000`
- **Probability (%)**: `30`
- **Response Status**: `Interested`

---

#### Step 5: Save

Click **"Save"**.

**Expected Results**:
1. ✅ Lead is created
2. ✅ **Common Open** = ✅ (checked, cannot be unchecked by non-sales)
3. ✅ **Assigned To** = (empty)
4. ✅ Lead appears in **"Open Leads"** menu
5. ✅ All salespeople can see this lead in "Open Leads"
6. ✅ Any salesperson can click "Take Lead" to claim it

---

### 6.3 Scenario C: Salesperson Takes an Open Lead

**User**: Bernard Leroy (BTP Salesperson)  
**Purpose**: Claim a common open lead and make it private.

**Navigation**: BTP Prospecting → Open Leads

---

#### Step 1: View Open Leads

1. Click **"BTP Prospecting"** menu
2. Click **"Open Leads"**
3. You should see the lead created by Chloe: "Hospital Renovation - Spraying"

---

#### Step 2: Open the Lead

1. Click on the lead name to open the form view
2. Notice:
   - **"Take Lead"** button is visible in the header (green/highlighted)
   - **"Assign"** button is also visible
   - **Common Open** checkbox is checked
   - **Assigned To** is empty

---

#### Step 3: Take the Lead

1. Click **"Take Lead"** button (top-left, highlighted)
2. A confirmation may appear (depending on configuration)
3. Lead form refreshes

**Expected Results**:
1. ✅ **"Take Lead"** button disappears (lead is no longer open)
2. ✅ **Common Open** checkbox is automatically **unchecked**
3. ✅ **Assigned To** field now shows **"Bernard Leroy"**
4. ✅ **Claimed Date** field (if visible) shows current date/time
5. ✅ Lead disappears from "Open Leads" menu
6. ✅ Lead appears in Bernard's personal lead list
7. ✅ Other salespeople can no longer see this lead (unless they are managers)

---

### 6.4 Scenario D: Create Lead with Web Form Origin

**User**: Alice Martin  
**Purpose**: Create a lead that came from the company website form.

**Navigation**: BTP Prospecting → Leads → Create

**Form Fields**:
- **Lead Title**: `Stadium Roof - Insulation`
- **Site Name**: `Stade Vélodrome`
- **Origin**: Select `Web Form`
- **Origin Detail**: `Submitted via website contact form on 2026-01-20`
- **Site Address**: `3 Boulevard Michelet, 13008 Marseille`
- **City**: `Marseille`
- **ZIP**: `13008`
- **Country**: `France`
- **Site Type**: `Infrastructure`
- **Client Name**: `Olympique de Marseille`
- **Email**: `contact@om.fr`
- **Phone**: `+33 4 91 76 45 45`
- **Estimated Budget**: `250000`
- **Probability (%)**: `35`
- **Response Status**: `Interested`
- **Next Reminder Date**: `Tomorrow`

**Save**.

**Expected Result**: 
- Lead assigned via round-robin (Marseille doesn't match Paris rule)
- Expected Revenue = 87,500 EUR (250,000 × 35%)

---

### 6.5 Scenario E: Create Lead with Partner Origin

**User**: Emma Petit (BTP Belgium)  
**Purpose**: Create a lead referred by a business partner.

**Prerequisites**: Create a partner "BTP Partner Network" in Contacts.

**Form Fields**:
- **Lead Title**: `Metro Extension - Waterproofing`
- **Site Name**: `Brussels Metro Line 3 Extension`
- **Origin**: Select `Partner`
- **Origin Detail**: `Referred by BTP Partner Network`
- **Site Address**: `Place de la Bourse, 1000 Brussels`
- **City**: `Brussels`
- **ZIP**: `1000`
- **Country**: `Belgium`
- **Site Type**: `Infrastructure`
- **Client Name**: `STIB (Brussels Public Transport)`
- **Email**: `info@stib.be`
- **Phone**: `+32 2 515 20 00`
- **Estimated Budget**: `300000`
- **Probability (%)**: `50`
- **Competitors**: Add `BESIX`, `Jan De Nul`
- **Response Status**: `Interested`
- **Next Reminder Date**: `Tomorrow`

**Multi-Company Tab**:
- **Sharing Type**: Select `Shared`
- **Shared Companies**: 
  - Check `BTP France`
  - Check `BTP Belgium`

**Save**.

**Expected Result**:
- Lead assigned to Emma (her company)
- Expected Revenue = 150,000 EUR
- Lead visible to both BTP France and BTP Belgium users (shared)

---

### 6.6 Scenario F: Create Lead with Public Tender Origin

**User**: David Roche (Manager)  
**Purpose**: Create a lead from a public tender announcement.

**Form Fields**:
- **Lead Title**: `School Renovation - Fire Safety`
- **Site Name**: `École Primaire Victor Hugo`
- **Origin**: Select `Public Tender`
- **Origin Detail**: `Tender published on BOAMP (Bulletin Officiel des Annonces de Marchés Publics) - Reference: 2026-001234`
- **Site Address**: `15 Rue Victor Hugo, 33000 Bordeaux`
- **City**: `Bordeaux`
- **ZIP**: `33000`
- **Country**: `France`
- **Site Type**: `Public Works`
- **Client Name**: `Mairie de Bordeaux`
- **Email**: `marches-publics@bordeaux.fr`
- **Phone**: `+33 5 56 10 20 30`
- **Tender Deadline**: `2026-03-31`
- **Estimated Budget**: `95000`
- **Probability (%)**: `25`
- **Response Status**: `Interested`
- **Response Note**: `Tender documents downloaded. Technical requirements reviewed. Need to prepare offer.`
- **Next Reminder Date**: `2026-01-25 10:00:00` (before tender deadline)

**Save**.

**Expected Result**:
- Lead assigned via round-robin (Bordeaux doesn't match Paris rule)
- Expected Revenue = 23,750 EUR
- Tender deadline visible in form

---

### 6.7 Scenario G: Create Lead with AI Auto-Search Origin

**User**: Alice Martin  
**Purpose**: Create a lead discovered through automated AI search (simulated).

**Form Fields**:
- **Lead Title**: `Shopping Mall - Thermal Insulation`
- **Site Name**: `Centre Commercial La Défense`
- **Origin**: Select `AI Auto-Search`
- **Origin Detail**: `AI detected construction permit application for thermal insulation project. Source: Paris city planning database.`
- **Site Address**: `15 Parvis de la Défense, 92092 Paris La Défense`
- **City**: `Paris`
- **ZIP**: `92092`
- **Country**: `France`
- **Site Type**: `Commercial`
- **Client Name**: `Unibail-Rodamco-Westfield`
- **Email**: `contact@urw.com`
- **Phone**: `+33 1 40 06 30 00`
- **Estimated Budget**: `220000`
- **Probability (%)**: `45`
- **Competitors**: Add `Saint-Gobain`, `Isover`
- **Response Status**: `Later`
- **Response Note**: `Project in early planning phase. Contact expected in Q2 2026.`
- **Next Reminder Date**: `2026-04-01 09:00:00`

**Save**.

**Expected Result**:
- Lead assigned to Alice (Paris geography rule)
- Expected Revenue = 99,000 EUR

---

### 6.8 Scenario H: Create Lead with Social Media Origin

**User**: Bernard Leroy  
**Purpose**: Create a lead discovered through social media monitoring.

**Form Fields**:
- **Lead Title**: `Warehouse Expansion - Spraying`
- **Site Name**: `Logistics Hub Nord`
- **Origin**: Select `Social Media`
- **Origin Detail**: `LinkedIn post by company CEO announcing expansion plans. Contacted via LinkedIn message.`
- **Site Address**: `Zone Industrielle Nord, 59000 Lille`
- **City**: `Lille`
- **ZIP**: `59000`
- **Country**: `France`
- **Site Type**: `Industrial`
- **Client Name**: `Logistics Solutions SA`
- **Email**: `info@logistics-solutions.fr`
- **Phone**: `+33 3 20 12 34 56`
- **Estimated Budget**: `150000`
- **Probability (%)**: `55`
- **Response Status**: `Interested`
- **Response Note**: `CEO responded positively. Meeting scheduled for next week.`
- **Next Reminder Date**: `Tomorrow`

**Save**.

**Expected Result**:
- Lead assigned via round-robin
- Expected Revenue = 82,500 EUR

---

### 6.9 Scenario I: Create Lead with File Import Origin

**User**: David Roche (Manager)  
**Purpose**: Create a lead imported from an Excel file or CSV.

**Form Fields**:
- **Lead Title**: `Bridge Renovation - Waterproofing`
- **Site Name**: `Pont de Normandie`
- **Origin**: Select `File Import`
- **Origin Detail**: `Imported from Excel file "Leads_2026_Q1.xlsx" - Row 42. Import date: 2026-01-20.`
- **Site Address**: `Pont de Normandie, 14600 Honfleur`
- **City**: `Honfleur`
- **ZIP**: `14600`
- **Country**: `France`
- **Site Type**: `Infrastructure`
- **Client Name**: `Direction Interdépartementale des Routes Normandie`
- **Email**: `contact@dir-normandie.fr`
- **Phone**: `+33 2 31 45 67 89`
- **Tender Deadline**: `2026-04-15`
- **Project Start Date**: `2026-05-01`
- **Project Duration**: `180`
- **Estimated Budget**: `500000`
- **Probability (%)**: `30`
- **Competitors**: Add `Colas`, `Eurovia`
- **Response Status**: `Interested`
- **Next Reminder Date**: `2026-01-25 14:00:00`

**Save**.

**Expected Result**:
- Lead assigned via round-robin
- Expected Revenue = 150,000 EUR

---

### 6.10 Scenario J: Create Lead with Referral Origin

**User**: Alice Martin  
**Purpose**: Create a lead referred by an existing client or contact.

**Form Fields**:
- **Lead Title**: `Office Building - Fireproofing`
- **Site Name**: `Tour Montparnasse Renovation`
- **Origin**: Select `Referral`
- **Origin Detail**: `Referred by Jean Dupont (Bouygues Batiment) - previous client.`
- **Site Address**: `33 Avenue du Maine, 75015 Paris`
- **City**: `Paris`
- **ZIP**: `75015`
- **Country**: `France`
- **Site Type**: `Commercial`
- **Client Name**: `Gecina`
- **Email**: `contact@gecina.fr`
- **Phone**: `+33 1 40 40 50 50`
- **Estimated Budget**: `280000`
- **Probability (%)**: `60` (higher because of referral)
- **Response Status**: `Interested`
- **Response Note**: `Warm referral from trusted client. High probability of success.`
- **Next Reminder Date**: `Tomorrow`

**Save**.

**Expected Result**:
- Lead assigned to Alice (Paris geography rule)
- Expected Revenue = 168,000 EUR

---

### 6.11 Scenario K: Create Lead with "Other" Origin

**User**: Bernard Leroy  
**Purpose**: Create a lead with custom origin not in the standard list.

**Form Fields**:
- **Lead Title**: `Residential Complex - Insulation`
- **Site Name**: `Résidence Les Jardins`
- **Origin**: Select `Other`
- **Origin Detail**: `Discovered during trade show "Batimat 2026". Business card exchange.`
- **Site Address**: `45 Avenue des Tilleuls, 69000 Lyon`
- **City**: `Lyon`
- **ZIP**: `69000`
- **Country**: `France`
- **Site Type**: `Residential`
- **Client Name**: `Promotion Immobilière Lyon`
- **Email**: `contact@promo-lyon.fr`
- **Phone**: `+33 4 78 12 34 56`
- **Estimated Budget**: `95000`
- **Probability (%)**: `35`
- **Response Status**: `Interested`
- **Next Reminder Date**: `Tomorrow`

**Save**.

**Expected Result**:
- Lead assigned via round-robin
- Expected Revenue = 33,250 EUR

---

### 6.12 Quick Reference: All Lead Fields

**Main Form**:
- Lead Title (required)
- Site Name
- Origin (required)
- Origin Detail
- Tags
- Assigned To
- Common Open
- Stage
- Qualification Status
- Converted (readonly)

**Site Information Tab**:
- Site Address
- City
- ZIP Code
- Country
- Site Type
- Project Start Date
- Project Duration
- Tender Deadline

**Client/Prospect Tab**:
- Client/Prospect (partner)
- Contact Person
- Client Name (if no partner)
- Email
- Phone

**Qualification Tab**:
- Estimated Budget
- Currency (auto)
- Probability (%)
- Expected Revenue (auto-calculated)
- Competitors
- Response Status
- Response Note

**Follow-up Tab**:
- Next Reminder Date
- Last Reminder Date (readonly)
- Reminder Count (readonly)
- Escalated (readonly)
- Escalation Date (readonly)
- Escalation Reason (readonly)

**Other Tabs**:
- Description
- Internal Notes
- Multi-Company
- Duplicates

---

## 7) Taking Open Leads - Scenarios

### 7.1 Scenario: Salesperson Takes a Single Open Lead

**User**: Bernard Leroy  
**Prerequisites**: Lead "Hospital Renovation - Spraying" exists as Common Open (created by Chloe in Scenario 6.2)

**Steps**:
1. **Login as Bernard**
2. Navigate to **BTP Prospecting → Open Leads**
3. **Find the lead** "Hospital Renovation - Spraying" in the list
4. **Click on the lead name** to open the form view
5. **Verify**:
   - "Take Lead" button is visible and highlighted (green)
   - "Common Open" checkbox is checked
   - "Assigned To" is empty
6. **Click "Take Lead"** button (top-left header)
7. **Wait for page refresh** (or confirmation if configured)

**Expected Results**:
- ✅ "Take Lead" button disappears
- ✅ "Common Open" automatically unchecked
- ✅ "Assigned To" now shows "Bernard Leroy"
- ✅ Lead disappears from "Open Leads" menu
- ✅ Lead appears in Bernard's lead list (BTP Prospecting → Leads)
- ✅ Other salespeople (except managers) cannot see this lead

**Verify in List View**:
1. Go to **BTP Prospecting → Leads**
2. Search for "Hospital Renovation"
3. Lead should appear with "Assigned To" = Bernard Leroy

---

### 7.2 Scenario: Manager Takes an Open Lead

**User**: David Roche (Manager)  
**Purpose**: Manager can also take open leads, same as salespeople.

**Steps**: Same as Scenario 7.1, but login as David.

**Expected Results**: Same as Scenario 7.1, but assigned to David.

---

### 7.3 Scenario: Multiple Salespeople View Same Open Lead

**Purpose**: Verify that multiple users can see the same open lead until one takes it.

**Test Steps**:
1. **Login as Alice**
2. Go to **BTP Prospecting → Open Leads**
3. **Note**: See lead "Hospital Renovation - Spraying" (if still open)
4. **Do NOT take it**, just note it exists
5. **Logout**
6. **Login as Bernard**
7. Go to **BTP Prospecting → Open Leads**
8. **Expected**: See the same lead
9. **Click "Take Lead"**
10. **Logout**
11. **Login as Alice** again
12. Go to **BTP Prospecting → Open Leads**
13. **Expected**: Lead is GONE (Bernard took it)
14. Go to **BTP Prospecting → Leads** (all leads)
15. **Expected**: Lead is NOT visible (Alice cannot see Bernard's private leads)

---

### 7.4 Scenario: Take Lead from Kanban View

**Alternative Method**: Take lead directly from Kanban view.

**Steps**:
1. Go to **BTP Prospecting → Open Leads**
2. **Switch to Kanban view** (if not already)
3. Find the lead card
4. **Click "Take Lead"** button on the card (if available)
   - OR open the lead and click "Take Lead" from form

**Expected Results**: Same as Scenario 7.1

---

## 8) Assigning Leads - Scenarios

### 8.1 Scenario: Manager Assigns Single Lead to Salesperson

**User**: David Roche (Manager)  
**Purpose**: Manager assigns an open lead or reassigns an existing lead.

**Prerequisites**: 
- Lead exists (can be open or assigned to someone else)
- Target salesperson exists (e.g., Alice or Bernard)

**Method 1: Assign from Lead Form**

**Steps**:
1. **Login as David**
2. Go to **BTP Prospecting → Leads** (or Open Leads)
3. **Open a lead** (e.g., "Hospital Renovation - Spraying")
4. **Click "Assign"** button (top-left header, next to "Take Lead")
5. **Modal dialog appears** with:
   - **Leads**: Shows current lead name (readonly, as a tag)
   - **Assign To**: Dropdown to select user
   - **Leave as Open**: Checkbox (if checked, lead remains Common Open)
6. **Select "Assign To"**: Choose `Alice Martin` from dropdown
7. **Leave "Leave as Open"**: Unchecked (lead will be assigned, not open)
8. **Click "Assign"** button in modal
9. **Modal closes automatically**
10. **Page refreshes**

**Expected Results**:
- ✅ Lead form shows "Assigned To" = Alice Martin
- ✅ "Common Open" is unchecked
- ✅ "Take Lead" button disappears
- ✅ Lead disappears from "Open Leads" (if it was there)
- ✅ Lead appears in Alice's lead list
- ✅ Assignment Rule field (if visible) may show "Manual Assignment"

---

**Method 2: Assign Multiple Leads from List View**

**Steps**:
1. **Login as David**
2. Go to **BTP Prospecting → Leads** (list view)
3. **Select multiple leads**:
   - Check the checkbox next to each lead you want to assign
   - Or use "Select All" if available
4. **Click "Action"** dropdown (top of list)
5. **Select "Assign Leads"** (or similar option)
6. **Modal appears** with:
   - **Leads**: Shows all selected leads (readonly tags)
   - **Assign To**: Dropdown
   - **Leave as Open**: Checkbox
7. **Select "Assign To"**: Choose `Bernard Leroy`
8. **Uncheck "Leave as Open"**
9. **Click "Assign"**

**Expected Results**:
- ✅ All selected leads are assigned to Bernard
- ✅ All leads show "Assigned To" = Bernard Leroy
- ✅ Modal closes
- ✅ List view refreshes

---

### 8.2 Scenario: Assign Lead and Keep as Open

**Purpose**: Assign a lead to someone but keep it visible to all (Common Open).

**Steps**:
1. Open a lead
2. Click **"Assign"**
3. Select **"Assign To"**: `Alice Martin`
4. **Check "Leave as Open"** checkbox
5. Click **"Assign"**

**Expected Results**:
- ✅ "Assigned To" = Alice Martin
- ✅ "Common Open" = ✅ (checked)
- ✅ Lead remains visible in "Open Leads"
- ✅ Other salespeople can still see it, but Alice is the primary owner

**Use Case**: When you want to assign responsibility but allow collaboration.

---

### 8.3 Scenario: Reassign Lead to Different User

**Purpose**: Transfer a lead from one salesperson to another.

**Prerequisites**: Lead "Tour Horizon - Fireproofing" is assigned to Alice

**Steps**:
1. **Login as David** (Manager)
2. Open lead "Tour Horizon - Fireproofing"
3. Click **"Assign"**
4. Select **"Assign To"**: `Bernard Leroy` (change from Alice)
5. Uncheck **"Leave as Open"**
6. Click **"Assign"**

**Expected Results**:
- ✅ "Assigned To" changes from Alice to Bernard
- ✅ Lead disappears from Alice's lead list
- ✅ Lead appears in Bernard's lead list
- ✅ Activity log (chatter) shows assignment change

---

### 8.4 Scenario: Salesperson Cannot Assign Leads

**Purpose**: Verify that only managers/admins can use "Assign" button.

**Test**:
1. **Login as Alice** (Salesperson, not manager)
2. Go to **BTP Prospecting → Open Leads**
3. Open an open lead
4. **Expected**: "Assign" button is **NOT visible** or **disabled**
5. **Expected**: Only "Take Lead" button is available

**Note**: Salespeople can only "Take" leads, not "Assign" them to others.

---

## 9) Setting Reminders - Scenarios

### 9.1 Scenario: Set Reminder Using "Set Reminder" Button

**User**: Alice Martin  
**Purpose**: Quickly set a reminder for today.

**Steps**:
1. **Login as Alice**
2. Open a lead (e.g., "Tour Horizon - Fireproofing")
3. **Click "Set Reminder"** button (top-right, calendar icon, in button box)
4. **Expected**: "Next Reminder Date" field is automatically set to current date/time
5. **Save** the lead (if not auto-saved)

**Expected Results**:
- ✅ "Next Reminder Date" is set to today's date and time
- ✅ Reminder will trigger when cron job runs (hourly)

---

### 9.2 Scenario: Set Reminder Manually in Follow-up Tab

**Purpose**: Set a specific future reminder date.

**Steps**:
1. Open a lead
2. Go to **"Follow-up"** tab
3. Click on **"Next Reminder Date"** field
4. **Select date and time**:
   - Date: `2026-01-25` (3 days from now)
   - Time: `10:00:00` (10 AM)
5. **Save** the lead

**Expected Results**:
- ✅ "Next Reminder Date" = 2026-01-25 10:00:00
- ✅ Reminder will be sent when this date/time is reached (cron runs hourly)

---

### 9.3 Scenario: Reminder Required at Stage

**Purpose**: Verify that reminders are mandatory at certain stages.

**Prerequisites**: 
- Stage "Qualified" has "Require Reminder" = Yes (see Section 4.2)

**Steps**:
1. Open a lead in "New" stage
2. Change **"Stage"** to **"Qualified"**
3. **Try to save** without setting "Next Reminder Date"
4. **Expected**: Error message appears: "Next reminder date is mandatory at this stage"
5. Go to **"Follow-up"** tab
6. Set **"Next Reminder Date"** = Tomorrow
7. **Save** again
8. **Expected**: Lead saves successfully

---

### 9.4 Scenario: View Reminder History

**Purpose**: Check how many reminders have been sent.

**Steps**:
1. Open a lead that has received reminders
2. Go to **"Follow-up"** tab
3. **View fields**:
   - **Last Reminder Date**: Shows date/time of last reminder sent
   - **Reminder Count**: Shows total number of reminders sent (e.g., 2)
   - **Next Reminder Date**: Shows when next reminder will be sent

**Example Values** (after 2 reminders):
- Last Reminder Date: `2026-01-20 09:00:00`
- Reminder Count: `2`
- Next Reminder Date: `2026-02-19 09:00:00` (30 days from last reminder)

---

### 9.5 Scenario: Test Reminder System Manually

**Purpose**: Trigger reminder cron immediately for testing (without waiting 1 hour).

**Method 1: Via Odoo Shell** (Recommended for testing)

**Steps**:
1. **Open terminal** on your server
2. **Navigate to Odoo directory**:
   ```bash
   cd /home/szymon/Documents/Odoo-BTP/odoo19
   ```
3. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```
4. **Run Odoo shell**:
   ```bash
   python3 odoo/odoo-bin shell -c odoo.conf -d odoo_btp
   ```
5. **In the Python shell, run**:
   ```python
   env['btp.lead']._cron_send_reminders()
   ```
6. **Exit shell**: Type `exit()` or press Ctrl+D

**Expected Results**:
- ✅ Reminders are sent for all leads where `next_reminder_date <= now`
- ✅ Mail activities are created
- ✅ Emails are sent (if user has email configured)
- ✅ "Last Reminder Date" and "Reminder Count" are updated
- ✅ "Next Reminder Date" is scheduled for next reminder (D0 → +15 → +30)

**Method 2: Wait for Automatic Cron**

- Cron runs **every 1 hour** automatically
- Check Odoo logs: `/home/szymon/Documents/Odoo-BTP/odoo19/logs/odoo.log`
- Look for: `Job 'BTP Lead: Send Reminders' (58) starting`

---

### 9.6 Scenario: Reminder Sequence (D0, +15, +30)

**Purpose**: Understand how reminder dates progress.

**Initial State** (new lead):
- Reminder Count: `0`
- Next Reminder Date: `2026-01-20 09:00:00` (today)

**After First Reminder** (D0 - Day 0):
- Cron runs and sends reminder
- Last Reminder Date: `2026-01-20 09:00:00`
- Reminder Count: `1`
- Next Reminder Date: `2026-01-20 09:00:00` (same day, or immediately)

**After Second Reminder** (+15 days):
- Cron runs 15 days later
- Last Reminder Date: `2026-02-04 09:00:00`
- Reminder Count: `2`
- Next Reminder Date: `2026-02-19 09:00:00` (15 days from now)

**After Third Reminder** (+30 days):
- Cron runs 30 days later
- Last Reminder Date: `2026-02-19 09:00:00`
- Reminder Count: `3`
- Next Reminder Date: `2026-03-21 09:00:00` (30 days from now)

**Subsequent Reminders**:
- All future reminders are scheduled **+30 days** from last reminder

---

### 9.7 Scenario: View Reminder Activity in Chatter

**Purpose**: See reminder notifications in the lead's activity log.

**Steps**:
1. Open a lead that received a reminder
2. **Scroll to "Activity" section** (right side, or bottom of form)
3. **Look for activity** with:
   - **Summary**: "Lead Reminder: D0" (or "+15", "+30")
   - **Assigned To**: The lead's assigned user
   - **Due Date**: Today's date
   - **Note**: "This lead requires follow-up. Next reminder was scheduled for [date]."

**Expected**: Activity appears in the chatter/activity log after reminder is sent.

---

## 10) Duplicate Detection and Merging - Scenarios

### 10.1 Scenario: Check for Duplicates Manually

**User**: Alice Martin  
**Purpose**: Check if a lead has potential duplicates in the system.

**Prerequisites**: 
- Lead "Tour Horizon - Fireproofing" exists (created in Scenario 6.1)
- Another similar lead exists (or create one first)

**Steps**:
1. **Login as Alice**
2. Open lead **"Tour Horizon - Fireproofing"**
3. **Click "Check Duplicates"** button (top-left header, next to "Assign")
4. **Two possible outcomes**:

**Outcome A: Duplicates Found**
- **Modal window opens** showing list of potential duplicates
- List shows: Lead name, Site name, Client, Assigned To, Stage
- **Click on a duplicate** to view it
- **Close modal** when done

**Outcome B: No Duplicates Found**
- **Notification appears**: "No Duplicates Found - No potential duplicates found for this lead."
- **Modal does not open**

**Expected Results**:
- ✅ System searches for duplicates based on:
  - Same or similar Site Address
  - Same Partner/Client
  - Same Site Name
- ✅ Duplicates appear in **"Duplicates"** tab of the lead form

---

### 10.2 Scenario: View Duplicates in Duplicates Tab

**Purpose**: See all potential duplicates for a lead.

**Steps**:
1. Open a lead that has duplicates detected
2. Go to **"Duplicates"** tab (bottom of form)
3. **View fields**:
   - **Is Duplicate**: Checkbox (mark this lead as a duplicate)
   - **Original Lead**: Dropdown (if Is Duplicate = Yes, select the original lead)
   - **Duplicates**: Readonly list showing all potential duplicates

**Duplicates List Columns**:
- Lead Title
- Site Name
- Client/Prospect
- Assigned To
- Stage

**Expected**: List shows all leads that match duplicate criteria.

---

### 10.3 Scenario: Mark Lead as Duplicate

**Purpose**: Flag a lead as a duplicate of another lead.

**Steps**:
1. Open a lead that is a duplicate
2. Go to **"Duplicates"** tab
3. **Check "Is Duplicate"** checkbox
4. **Select "Original Lead"**: Choose the original lead from dropdown
5. **Save** the lead

**Expected Results**:
- ✅ "Is Duplicate" = ✅ (checked)
- ✅ "Original Lead" = [selected lead]
- ✅ Lead may be visually marked as duplicate in list view (red decoration)

---

### 10.4 Scenario: Merge Two Duplicate Leads

**User**: David Roche (Manager)  
**Purpose**: Merge duplicate leads into one, preserving history.

**Prerequisites**: 
- Two duplicate leads exist:
  - Lead A: "Tour Horizon - Fireproofing" (original)
  - Lead B: "Tour Horizon Fireproofing" (duplicate, slightly different name)

**Steps**:
1. **Login as David** (Manager or Admin)
2. Go to **BTP Prospecting → Leads** (list view)
3. **Select both leads**:
   - Check checkbox next to Lead A
   - Check checkbox next to Lead B
4. **Click "Action"** dropdown (top of list)
5. **Select "Merge Leads"** (or "Merge" option)
6. **Merge Wizard opens** with:
   - **Leads to Merge**: Shows both selected leads (readonly)
   - **Target Lead**: Dropdown to select which lead to keep
   - **Merge Strategy**: 
     - `Keep Target` - Keep only target lead data
     - `Keep Newest` - Keep data from most recently created lead
     - `Merge` - Combine data from both leads
7. **Select "Target Lead"**: Choose `Tour Horizon - Fireproofing` (Lead A)
8. **Select "Merge Strategy"**: Choose `Merge` (to combine all data)
9. **Click "Merge"** button
10. **Confirmation dialog**: Click "Confirm" if asked

**Expected Results**:
- ✅ Lead B is deleted (or marked as merged)
- ✅ Lead A contains combined data from both leads
- ✅ Activity log shows merge history
- ✅ All related records (activities, emails, etc.) are preserved

**Verify**:
1. Open the remaining lead (Lead A)
2. Check that it contains data from both original leads
3. Check activity log for merge notification

---

### 10.5 Scenario: Automatic Duplicate Detection on Creation

**Purpose**: System automatically detects duplicates when creating a new lead.

**Steps**:
1. Create a new lead with:
   - Site Address: `21 Rue de Rivoli` (same as existing lead)
   - Client Name: `Bouygues Batiment` (same as existing lead)
2. **Save** the lead
3. **Expected**: System may show a warning or automatically detect duplicates
4. Open the lead
5. Go to **"Duplicates"** tab
6. **Expected**: Duplicate leads appear in the list

**Note**: Exact behavior depends on module configuration. Some systems show warnings, others just populate the Duplicates tab.

---

## 11) Converting Leads to Opportunities

### 11.1 Scenario: Convert Qualified Lead to CRM Opportunity

**User**: Alice Martin  
**Purpose**: Convert a qualified lead to a CRM opportunity for sales pipeline management.

**Prerequisites**: 
- Lead "Tour Horizon - Fireproofing" exists and is qualified
- Lead is in "Qualified" or later stage
- Lead is assigned to Alice

**Steps**:
1. **Login as Alice**
2. Open lead **"Tour Horizon - Fireproofing"**
3. **Verify lead is ready for conversion**:
   - Stage = "Qualified" or later
   - Budget and probability are set
   - Client information is complete
4. **Click "Convert to Opportunity"** button (top-left header, highlighted)
5. **Confirmation dialog may appear** - Click "Confirm" if asked
6. **Page may redirect** to the created opportunity, or show a notification

**Expected Results**:
- ✅ Lead is marked as "Converted" (checkbox checked, readonly)
- ✅ **"Convert to Opportunity"** button disappears (lead already converted)
- ✅ **"Converted Date"** field shows current date/time
- ✅ **"Opportunity ID"** field (if visible) shows link to created opportunity
- ✅ A new CRM opportunity is created with:
  - Same name as lead
  - Same partner/client
  - Same budget and probability
  - Same assigned user
- ✅ Opportunity appears in CRM app

**Verify Conversion**:
1. Go to **CRM** app (from app switcher)
2. Go to **Opportunities**
3. **Expected**: See "Tour Horizon - Fireproofing" opportunity
4. Open the opportunity
5. **Expected**: Contains data from the original lead

---

### 11.2 Scenario: Cannot Convert Unqualified Lead

**Purpose**: Verify that only qualified leads can be converted.

**Test**:
1. Open a lead in "New" stage
2. **Expected**: "Convert to Opportunity" button may be disabled or show a warning
3. Move lead to "Qualified" stage
4. **Expected**: "Convert to Opportunity" button becomes enabled

**Note**: Exact behavior depends on module configuration. Some systems allow conversion at any stage, others require qualification.

---

### 11.3 Scenario: View Converted Lead Information

**Purpose**: See conversion details in the lead form.

**Steps**:
1. Open a converted lead
2. **Check fields** (may be in a separate section or tab):
   - **Converted**: ✅ (checked, readonly)
   - **Converted Date**: Shows date/time of conversion
   - **Opportunity ID**: Link to the created opportunity (clickable)
   - **Quote ID**: (if quote was created from opportunity)

**Expected**: All conversion information is visible and linked.

---

## 12) Multi-Company Sharing - Scenarios

### 12.1 Scenario: Create Exclusive Lead (Default)

**User**: Alice Martin (BTP France)  
**Purpose**: Create a lead that is only visible to BTP France users.

**Steps**:
1. **Login as Alice**
2. Create a new lead (see Section 6.1 for details)
3. Go to **"Multi-Company"** tab
4. **Verify fields**:
   - **Company**: `BTP France` (auto-filled from user's company)
   - **Sharing Type**: `Exclusive` (default)
   - **Shared Companies**: (field is hidden when Exclusive)
5. **Save** the lead

**Expected Results**:
- ✅ Lead is only visible to users from BTP France
- ✅ Users from BTP Belgium (e.g., Emma) cannot see this lead
- ✅ BTP Administrator can see it (admins see all companies)

---

### 12.2 Scenario: Share Lead with Specific Companies

**User**: Emma Petit (BTP Belgium)  
**Purpose**: Share a lead between BTP France and BTP Belgium.

**Prerequisites**: Lead "Metro Extension - Waterproofing" exists (created in Scenario 6.5)

**Steps**:
1. **Login as Emma**
2. Open lead **"Metro Extension - Waterproofing"**
3. Go to **"Multi-Company"** tab
4. **Change "Sharing Type"**: Select `Shared` from dropdown
5. **"Shared Companies"** field appears
6. **Click "Add a line"** in Shared Companies
7. **Select companies**:
   - Check `BTP France`
   - Check `BTP Belgium` (if you want to include your own company)
8. **Save** the lead

**Expected Results**:
- ✅ Sharing Type = `Shared`
- ✅ Shared Companies = BTP France, BTP Belgium
- ✅ Users from both companies can see this lead
- ✅ Users from other companies cannot see it

**Verify**:
1. **Logout** and **Login as Alice** (BTP France)
2. Go to **BTP Prospecting → Leads**
3. **Expected**: Can see "Metro Extension - Waterproofing" lead
4. **Logout** and **Login as Emma** (BTP Belgium)
5. Go to **BTP Prospecting → Leads**
6. **Expected**: Can also see the lead

---

### 12.3 Scenario: Create Global Lead (All Companies)

**User**: David Roche (Manager)  
**Purpose**: Create a lead visible to all companies.

**Steps**:
1. **Login as David**
2. Create a new lead
3. Go to **"Multi-Company"** tab
4. **Change "Sharing Type"**: Select `Global` from dropdown
5. **Save** the lead

**Expected Results**:
- ✅ Sharing Type = `Global`
- ✅ Lead is visible to users from ALL companies
- ✅ No company restrictions

**Note**: "Global" sharing type may not be available in all configurations. If not available, use "Shared" and select all companies.

---

### 12.4 Scenario: Change Sharing Type of Existing Lead

**Purpose**: Modify sharing settings for an existing lead.

**Steps**:
1. Open an existing lead
2. Go to **"Multi-Company"** tab
3. **Change "Sharing Type"**: 
   - From `Exclusive` to `Shared`
   - Or from `Shared` to `Exclusive`
4. **Update "Shared Companies"** if needed
5. **Save** the lead

**Expected Results**:
- ✅ Sharing settings are updated immediately
- ✅ Visibility changes apply to all users
- ✅ Users may need to refresh their view to see changes

---

## 13) Reminder System Testing - Complete Guide

### 13.1 Scenario: Test D0 Reminder (Day 0 - Immediate)

**Purpose**: Test that reminders are sent when `next_reminder_date` is in the past.

**Prerequisites**: Lead exists with assigned user

**Steps**:
1. **Open a lead** (e.g., "Tour Horizon - Fireproofing")
2. Go to **"Follow-up"** tab
3. **Set "Next Reminder Date"**: 
   - Date: `Today`
   - Time: `1 hour ago` (e.g., if now is 10:00, set to 09:00)
4. **Save** the lead
5. **Wait for cron** (runs hourly) OR **trigger manually** (see Section 9.5)
6. **Check results**:
   - Go to **"Follow-up"** tab
   - **Last Reminder Date**: Should show the time reminder was sent
   - **Reminder Count**: Should be `1` (was 0, now 1)
   - **Next Reminder Date**: Should be set to `15 days from now`
7. **Check Activity**:
   - Go to **"Activity"** section (chatter)
   - **Expected**: See activity "Lead Reminder: D0"
   - **Assigned To**: Lead's assigned user
   - **Due Date**: Today
8. **Check Email** (if user has email configured):
   - Assigned user should receive email notification
   - Email subject: "Lead Reminder: [Lead Name]"

**Expected Results**:
- ✅ Reminder sent successfully
- ✅ Activity created
- ✅ Email sent (if configured)
- ✅ Next reminder scheduled for +15 days

---

### 13.2 Scenario: Test +15 Days Reminder

**Purpose**: Verify that second reminder is sent 15 days after first.

**Prerequisites**: Lead has received first reminder (Reminder Count = 1)

**Steps**:
1. **Open a lead** that has Reminder Count = 1
2. Go to **"Follow-up"** tab
3. **Note current "Next Reminder Date"**: Should be approximately 15 days from last reminder
4. **Manually set "Next Reminder Date"** to a past date (to trigger immediately):
   - Set to `1 hour ago`
5. **Save** the lead
6. **Trigger reminder cron** (manually or wait)
7. **Check results**:
   - **Last Reminder Date**: Updated to current time
   - **Reminder Count**: Should be `2` (was 1, now 2)
   - **Next Reminder Date**: Should be set to `30 days from now`
8. **Check Activity**:
   - **Expected**: See activity "Lead Reminder: +15"

**Expected Results**:
- ✅ Second reminder sent
- ✅ Reminder Count = 2
- ✅ Next reminder scheduled for +30 days

---

### 13.3 Scenario: Test +30 Days Reminder

**Purpose**: Verify that third and subsequent reminders are sent every 30 days.

**Prerequisites**: Lead has Reminder Count = 2

**Steps**:
1. **Open a lead** with Reminder Count = 2
2. **Set "Next Reminder Date"** to past date
3. **Trigger reminder cron**
4. **Check results**:
   - **Reminder Count**: Should be `3`
   - **Next Reminder Date**: Should be `30 days from now` (not 15)
5. **Check Activity**: Should show "Lead Reminder: +30"

**Expected Results**:
- ✅ Third reminder sent
- ✅ All future reminders scheduled for +30 days

---

### 13.4 Scenario: Test Reminder for Unassigned Lead

**Purpose**: Verify that reminders are not sent if lead has no assigned user.

**Steps**:
1. **Create an open lead** (Common Open = Yes, Assigned To = empty)
2. **Set "Next Reminder Date"** to past date
3. **Trigger reminder cron**
4. **Check results**:
   - **Expected**: Reminder is NOT sent (lead has no user_id)
   - **Reminder Count**: Remains 0
   - **Last Reminder Date**: Remains empty

**Expected Results**:
- ✅ No reminder sent (system requires assigned user)
- ✅ No activity created
- ✅ No email sent

---

### 13.5 Scenario: View Reminder History

**Purpose**: See complete reminder history for a lead.

**Steps**:
1. Open a lead that has received multiple reminders
2. Go to **"Follow-up"** tab
3. **View summary**:
   - **Reminder Count**: Total number (e.g., 3)
   - **Last Reminder Date**: Most recent reminder time
   - **Next Reminder Date**: When next reminder will be sent
4. Go to **"Activity"** section
5. **Filter activities** by type "Reminder" or search for "Reminder"
6. **Expected**: See all reminder activities in chronological order:
   - "Lead Reminder: D0" (first)
   - "Lead Reminder: +15" (second)
   - "Lead Reminder: +30" (third, and subsequent)

**Expected Results**:
- ✅ Complete reminder history visible
- ✅ Activities show reminder type and date
- ✅ Easy to track follow-up frequency

---

### 13.6 Scenario: Manual Reminder Trigger (For Testing)

**Purpose**: Trigger reminders immediately without waiting for cron.

**Method: Odoo Shell** (See Section 9.5 for detailed steps)

**Quick Command**:
```bash
cd /home/szymon/Documents/Odoo-BTP/odoo19
source venv/bin/activate
python3 odoo/odoo-bin shell -c odoo.conf -d odoo_btp
```

Then in Python shell:
```python
# Send reminders for all due leads
env['btp.lead']._cron_send_reminders()

# Check how many leads need reminders
leads = env['btp.lead'].search([
    ('active', '=', True),
    ('converted', '=', False),
    ('next_reminder_date', '<=', env['btp.lead']._fields['next_reminder_date'].now()),
    ('next_reminder_date', '!=', False),
])
print(f"Leads needing reminders: {len(leads)}")

# Exit
exit()
```

**Expected Results**:
- ✅ Reminders sent immediately
- ✅ Activities created
- ✅ Emails sent (if configured)
- ✅ Reminder counts updated

---

## 14) Escalation System - Scenarios

### 14.1 Scenario: Lead Escalates After 30+ Days Without Update

**Purpose**: Verify that stalled leads are escalated to management.

**Prerequisites**: 
- Lead exists with assigned user
- Lead has not been updated for 30+ days
- Lead has received reminders (last_reminder_date is set)

**Steps**:
1. **Create or find a lead** that:
   - Has `last_reminder_date` = 31 days ago (or more)
   - Has `is_escalated` = False
   - Is active and not converted
2. **Trigger escalation cron** (runs daily, or trigger manually):
   ```python
   env['btp.lead']._cron_escalate_leads()
   ```
3. **Check lead**:
   - Open the lead
   - Go to **"Follow-up"** tab
   - **Expected**:
     - **Escalated**: ✅ (checked)
     - **Escalation Date**: Shows current date/time
     - **Escalation Reason**: "Lead stalled for 30+ days without update"
4. **Check manager's activity**:
   - **Login as David** (Manager, or lead's user's manager)
   - Go to **Activities** (or lead's activity section)
   - **Expected**: See activity "Lead Escalation: Stalled Lead"
   - **Assigned To**: Manager
   - **Note**: "This lead has been stalled for 30+ days and requires management attention."

**Expected Results**:
- ✅ Lead marked as escalated
- ✅ Activity created for manager
- ✅ Email sent to manager (if configured)
- ✅ Manager can review and take action

---

### 14.2 Scenario: View Escalated Lead

**Purpose**: Identify escalated leads in the system.

**Method 1: Filter in List View**

**Steps**:
1. Go to **BTP Prospecting → Leads** (list view)
2. **Click "Filters"** dropdown
3. **Add filter**: "Escalated" = "Yes"
4. **Expected**: List shows only escalated leads
5. **Visual indicator**: Escalated leads may show warning decoration (yellow/orange)

**Method 2: Check Lead Form**

**Steps**:
1. Open any lead
2. Go to **"Follow-up"** tab
3. **Check "Escalated"** field:
   - ✅ = Lead is escalated
   - ☐ = Lead is not escalated

---

### 14.3 Scenario: Manager Reviews Escalated Lead

**User**: David Roche (Manager)  
**Purpose**: Manager takes action on an escalated lead.

**Steps**:
1. **Login as David**
2. **View escalated leads** (use filter from Scenario 14.2)
3. **Open an escalated lead**
4. **Review information**:
   - Check **"Escalation Date"** and **"Escalation Reason"**
   - Review lead history and activities
   - Check last update date
5. **Take action**:
   - **Option A**: Reassign to different salesperson
     - Click **"Assign"**
     - Select new user
   - **Option B**: Take the lead yourself
     - Click **"Take Lead"** (if lead is open) or **"Assign"** to yourself
   - **Option C**: Add notes and schedule follow-up
     - Add activity or note in chatter
     - Set new reminder date
6. **Save** changes

**Expected Results**:
- ✅ Manager can see all escalated leads
- ✅ Manager can reassign or take action
- ✅ Lead status can be updated

---

## 15) Round-Robin Assignment Testing

### 15.1 Scenario: Test Round-Robin with Different Weights

**Purpose**: Verify that users with higher weights receive more leads.

**Prerequisites**: 
- Alice has weight = 2
- Bernard has weight = 1
- Emma has weight = 1
- Round-robin rule is configured (Priority 10)

**Steps**:
1. **Create multiple leads** that don't match geography rule (e.g., City = "Lyon"):
   - Lead 1: City = Lyon → Should assign to first in pool
   - Lead 2: City = Lyon → Should assign to second in pool
   - Lead 3: City = Lyon → Should assign to third in pool
   - Lead 4: City = Lyon → Should assign to fourth in pool
   - And so on...
2. **Count assignments**:
   - Check how many leads Alice received
   - Check how many leads Bernard received
   - Check how many leads Emma received

**Expected Results** (with weights 2, 1, 1):
- ✅ Alice receives approximately **2x more leads** than Bernard or Emma
- ✅ Distribution: Alice, Alice, Bernard, Emma, Alice, Alice, Bernard, Emma...
- ✅ Pattern repeats based on weights

---

### 15.2 Scenario: Test Round-Robin with Unavailable User

**Purpose**: Verify that unavailable users are excluded from round-robin.

**Steps**:
1. **Set Alice as Unavailable** (Section 2.4)
2. **Create leads** that trigger round-robin
3. **Expected**: Alice should NOT receive any leads
4. **Expected**: Only Bernard and Emma receive leads (equal distribution, weight 1 each)
5. **Set Alice as Available** (uncheck Unavailable)
6. **Create more leads**
7. **Expected**: Alice starts receiving leads again (with weight 2)

---

### 15.3 Scenario: Test Round-Robin with Overloaded User

**Purpose**: Verify that overloaded users receive fewer leads.

**Steps**:
1. **Set Bernard as Overloaded** (Section 2.4)
2. **Create leads** that trigger round-robin
3. **Expected**: Bernard receives fewer leads than normal
4. **Expected**: Alice and Emma receive more leads (to compensate)
5. **Uncheck Overloaded** for Bernard
6. **Expected**: Normal distribution resumes

---

## 16) Pyramidal Visibility Testing

### 16.1 Scenario: Manager Sees Subordinate Leads

**User**: David Roche (Manager)  
**Purpose**: Verify that managers can see all leads from their subordinates.

**Prerequisites**: 
- David is manager of Alice and Bernard
- Alice has a lead: "Tour Horizon - Fireproofing"
- Bernard has a lead: "Hospital Renovation - Spraying"

**Steps**:
1. **Login as David**
2. Go to **BTP Prospecting → Leads**
3. **Expected**: Can see both leads:
   - "Tour Horizon - Fireproofing" (Assigned To = Alice)
   - "Hospital Renovation - Spraying" (Assigned To = Bernard)
4. **Open each lead**
5. **Expected**: Can view and edit both leads

**Expected Results**:
- ✅ Manager sees all subordinate leads
- ✅ Manager can edit and reassign subordinate leads

---

### 16.2 Scenario: Salesperson Cannot See Peer Leads

**User**: Alice Martin  
**Purpose**: Verify that salespeople cannot see each other's leads.

**Steps**:
1. **Login as Alice**
2. Go to **BTP Prospecting → Leads**
3. **Expected**: Can see:
   - ✅ "Tour Horizon - Fireproofing" (her own lead)
   - ❌ "Hospital Renovation - Spraying" (Bernard's lead) - NOT visible
4. **Search for "Hospital"**
5. **Expected**: No results (lead is not visible to Alice)

**Expected Results**:
- ✅ Salespeople only see their own leads
- ✅ Salespeople cannot see peer leads
- ✅ Exception: Common Open leads are visible to all

---

### 16.3 Scenario: Manager Hierarchy (Multi-Level)

**Purpose**: Test multi-level manager hierarchy (if configured).

**Example Structure**:
- CEO (top manager)
  - Regional Manager (David)
    - Salesperson (Alice)
    - Salesperson (Bernard)

**Expected**:
- ✅ CEO sees all leads (from Regional Manager, Alice, Bernard)
- ✅ Regional Manager (David) sees Alice and Bernard's leads
- ✅ Alice and Bernard only see their own leads

**Note**: This requires additional manager hierarchy configuration beyond basic setup.

---

## 17) Open Leads Queue - Detailed Scenarios

### 17.1 Scenario: View All Open Leads

**Purpose**: See all common open leads in one place.

**Steps**:
1. Go to **BTP Prospecting → Open Leads**
2. **Expected**: List shows all leads where:
   - **Common Open** = ✅ (checked)
   - **Assigned To** = (empty)
3. **View options**:
   - **List view**: Table format
   - **Kanban view**: Card format (if available)
4. **Columns/Fields visible**:
   - Lead Title
   - Site Name
   - Client/Prospect
   - Stage
   - Created Date
   - Created By

**Expected Results**:
- ✅ All open leads visible
- ✅ Easy to browse and select leads to take

---

### 17.2 Scenario: Filter Open Leads

**Purpose**: Find specific open leads using filters.

**Steps**:
1. Go to **BTP Prospecting → Open Leads**
2. **Click "Filters"** dropdown
3. **Add filters** (examples):
   - **Origin** = "Web Form"
   - **City** = "Paris"
   - **Site Type** = "Commercial"
   - **Created Date** = "Last 7 days"
4. **Apply filters**
5. **Expected**: List shows only matching open leads

**Use Case**: Find leads from specific sources or locations.

---

### 17.3 Scenario: Sort Open Leads

**Purpose**: Organize open leads by priority or date.

**Steps**:
1. Go to **BTP Prospecting → Open Leads** (list view)
2. **Click column header** to sort:
   - **Created Date**: Newest first or oldest first
   - **Lead Title**: Alphabetical
   - **Budget**: Highest first or lowest first
3. **Expected**: List reorders based on selected column

**Use Case**: Prioritize leads by creation date or budget.

---

## 18) Reports

### 18.1 Scenario: Print Lead Report

**Purpose**: Generate a printable report for a lead.

**Steps**:
1. **Open a lead** (e.g., "Tour Horizon - Fireproofing")
2. **Click "Print"** button (top-right, printer icon)
3. **Select report**: Choose **"BTP Lead Report"** from dropdown
4. **Click "Print"** or **"PDF"** (depending on option)
5. **Report opens** in new window/tab

**Report Contents** (expected):
- Lead Title
- Site Information (name, address, city, country)
- Client/Prospect Information
- Qualification Details (budget, probability, expected revenue)
- Stage and Status
- Assigned To
- Dates (created, reminder, etc.)
- Notes and Description

**Use Cases**:
- Print for meetings
- Email to stakeholders
- Archive documentation
- Share with team members

---

## 19) Spec Alignment - What Exists vs. What is Not Yet

### 19.1 Implemented Features

**✅ Lead Management**:
- Lead creation from UI (all origin types)
- Lead editing and updating
- Lead deletion (with proper access control)
- Lead stages and workflow
- Qualification status tracking

**✅ Assignment & Visibility**:
- Automatic assignment rules (geography, client type, site type, round-robin, manual)
- Common Open leads (visible to all until claimed)
- Take Lead functionality
- Manual assignment (manager action)
- Pyramidal visibility (managers see subordinates' leads)
- Multi-company sharing (exclusive, shared, global)

**✅ Follow-up & Reminders**:
- Manual reminder setting
- Automated reminders (D0, +15, +30 days)
- Reminder scheduling based on stage
- Reminder count tracking
- Email notifications (if configured)
- Activity creation for reminders

**✅ Escalation**:
- Automatic escalation after 30+ days without update
- Escalation to manager
- Escalation activity and email
- Escalation reason tracking

**✅ Duplicate Management**:
- Automatic duplicate detection on creation
- Manual duplicate checking
- Duplicate marking and linking
- Merge wizard with history preservation
- Duplicate list in lead form

**✅ Integration**:
- Conversion to CRM opportunity
- Messaging and chatter integration
- Email integration
- Activity tracking

**✅ Multi-Channel Lead Capture**:
- UI creation (all origin types)
- Public web form endpoint `/btp/lead/create` (requires website templates)
- Mobile JSON endpoint `/btp/lead/mobile` (for mobile app integration)

**✅ Configuration**:
- Customizable lead stages
- Assignment rules configuration
- User groups and permissions
- Round-robin weights and availability settings

---

### 19.2 Not Yet Implemented

**❌ Advanced AI Features**:
- Real AI lead search/enrichment (currently "AI Auto-Search" is only a label in Origin)
- Automatic lead data enrichment from external sources
- AI-powered duplicate detection (beyond basic matching)
- Predictive scoring based on AI

**❌ Advanced Analytics**:
- KPI dashboards (conversion rates, pipeline value, etc.)
- Pipeline analytics and forecasting
- Performance reports by user/team
- Lead source analysis
- Aging analysis reports

**❌ Advanced Activity Tracking**:
- Dedicated call logging interface (beyond basic activities)
- Meeting scheduling and tracking (beyond basic activities)
- Visit logging with GPS/location
- Activity templates

**❌ Advanced Workflow**:
- Escalation queue or reassign board (visual interface)
- Automated workflow actions based on conditions
- Lead scoring automation
- Stage transition automation

**❌ Advanced Reporting**:
- Custom report builder
- Scheduled report delivery
- Export to Excel/CSV with custom formats
- Graphical dashboards

**Note**: These features may be added in future module versions or as separate modules.

---

## 20) Quick Mock Dataset - Copy/Paste

### Complete Lead Dataset for Testing

Use these exact values to quickly create test leads:

---

#### Lead 1: Commercial Fireproofing (Paris)

**Main Form**:
- **Lead Title**: `Tour Horizon - Fireproofing`
- **Site Name**: `Tour Horizon`
- **Origin**: `Field Discovery`
- **Origin Detail**: `On-site visit during routine inspection`
- **Assigned To**: `Alice Martin` (or leave empty for auto-assignment)
- **Stage**: `New`
- **Qualification Status**: `Field`

**Site Information**:
- **Site Address**: `21 Rue de Rivoli, 75001 Paris`
- **City**: `Paris`
- **ZIP Code**: `75001`
- **Country**: `France`
- **Site Type**: `Commercial`
- **Project Start Date**: `2026-03-15`
- **Project Duration**: `120`
- **Tender Deadline**: `2026-02-28`

**Client/Prospect**:
- **Client Name**: `Bouygues Batiment`
- **Email**: `j.dupont@bouygues.fr`
- **Phone**: `+33 6 11 22 33 44`

**Qualification**:
- **Estimated Budget**: `180000`
- **Probability (%)**: `40`
- **Expected Revenue**: `72000` (auto-calculated)
- **Competitors**: `Vinci`, `Eiffage`
- **Response Status**: `Later`
- **Response Note**: `Client will reopen tender in March.`

**Follow-up**:
- **Next Reminder Date**: `Tomorrow`

---

#### Lead 2: Stadium Insulation (Marseille - Open)

**Main Form**:
- **Lead Title**: `Stadium Roof - Insulation`
- **Site Name**: `Stade Vélodrome`
- **Origin**: `Web Form`
- **Origin Detail**: `Submitted via website contact form`
- **Common Open**: ✅ (checked)
- **Assigned To**: (empty)
- **Stage**: `New`

**Site Information**:
- **Site Address**: `3 Boulevard Michelet, 13008 Marseille`
- **City**: `Marseille`
- **ZIP Code**: `13008`
- **Country**: `France`
- **Site Type**: `Infrastructure`

**Client/Prospect**:
- **Client Name**: `Olympique de Marseille`
- **Email**: `contact@om.fr`
- **Phone**: `+33 4 91 76 45 45`

**Qualification**:
- **Estimated Budget**: `250000`
- **Probability (%)**: `35`
- **Expected Revenue**: `87500` (auto)
- **Response Status**: `Interested`

**Follow-up**:
- **Next Reminder Date**: `Tomorrow`

---

#### Lead 3: Hospital Renovation (Lyon)

**Main Form**:
- **Lead Title**: `Hospital Renovation - Spraying`
- **Site Name**: `Hôpital Edouard Herriot`
- **Origin**: `Manual Entry`
- **Origin Detail**: `Received via phone call`
- **Assigned To**: `Bernard Leroy` (or leave empty)
- **Stage**: `New`

**Site Information**:
- **Site Address**: `5 Place d'Arsonval, 69003 Lyon`
- **City**: `Lyon`
- **ZIP Code**: `69003`
- **Country**: `France`
- **Site Type**: `Public Works`

**Client/Prospect**:
- **Client Name**: `Hospices Civils de Lyon`
- **Email**: `contact@chu-lyon.fr`
- **Phone**: `+33 4 72 11 69 11`

**Qualification**:
- **Estimated Budget**: `120000`
- **Probability (%)**: `30`
- **Expected Revenue**: `36000` (auto)
- **Response Status**: `Interested`

**Follow-up**:
- **Next Reminder Date**: `Tomorrow`

---

#### Lead 4: Metro Waterproofing (Brussels - Shared)

**Main Form**:
- **Lead Title**: `Metro Extension - Waterproofing`
- **Site Name**: `Brussels Metro Line 3 Extension`
- **Origin**: `Partner`
- **Origin Detail**: `Referred by BTP Partner Network`
- **Assigned To**: `Emma Petit` (BTP Belgium)
- **Stage**: `New`

**Site Information**:
- **Site Address**: `Place de la Bourse, 1000 Brussels`
- **City**: `Brussels`
- **ZIP Code**: `1000`
- **Country**: `Belgium`
- **Site Type**: `Infrastructure`

**Client/Prospect**:
- **Client Name**: `STIB (Brussels Public Transport)`
- **Email**: `info@stib.be`
- **Phone**: `+32 2 515 20 00`

**Qualification**:
- **Estimated Budget**: `300000`
- **Probability (%)**: `50`
- **Expected Revenue**: `150000` (auto)
- **Competitors**: `BESIX`, `Jan De Nul`
- **Response Status**: `Interested`

**Multi-Company**:
- **Sharing Type**: `Shared`
- **Shared Companies**: `BTP France`, `BTP Belgium`

**Follow-up**:
- **Next Reminder Date**: `Tomorrow`

---

#### Lead 5: School Fire Safety (Bordeaux - Public Tender)

**Main Form**:
- **Lead Title**: `School Renovation - Fire Safety`
- **Site Name**: `École Primaire Victor Hugo`
- **Origin**: `Public Tender`
- **Origin Detail**: `Tender published on BOAMP - Reference: 2026-001234`
- **Stage**: `New`

**Site Information**:
- **Site Address**: `15 Rue Victor Hugo, 33000 Bordeaux`
- **City**: `Bordeaux`
- **ZIP Code**: `33000`
- **Country**: `France`
- **Site Type**: `Public Works`
- **Tender Deadline**: `2026-03-31`

**Client/Prospect**:
- **Client Name**: `Mairie de Bordeaux`
- **Email**: `marches-publics@bordeaux.fr`
- **Phone**: `+33 5 56 10 20 30`

**Qualification**:
- **Estimated Budget**: `95000`
- **Probability (%)**: `25`
- **Expected Revenue**: `23750` (auto)
- **Response Status**: `Interested`
- **Response Note**: `Tender documents downloaded. Technical requirements reviewed.`

**Follow-up**:
- **Next Reminder Date**: `2026-01-25 10:00:00`

---

### Quick Creation Tips

1. **Copy the values above** for each lead
2. **Create lead** in BTP Prospecting → Leads → Create
3. **Paste values** into corresponding fields
4. **Save** and verify assignment

**Note**: Some fields may auto-fill or auto-calculate (e.g., Expected Revenue, Assigned To based on rules).

---

## 21) Troubleshooting

### 21.1 "I Cannot See BTP Prospecting in the Menu"

**Symptoms**: 
- BTP Prospecting does not appear in app switcher
- Menu items are missing

**Possible Causes & Solutions**:

**Cause 1: Module Not Installed**
- **Solution**: 
  1. Go to **Apps** (from app switcher)
  2. Click **"Installed"** filter
  3. Search for "BTP Prospecting"
  4. If not found, click **"Update Apps List"**
  5. Search again and click **"Install"** if needed

**Cause 2: User Missing Access Rights**
- **Solution**:
  1. **Login as Administrator**
  2. Go to **Settings → Users & Companies → Users**
  3. Open your user
  4. Go to **"Access Rights"** tab
  5. Check one of these groups:
     - **BTP Administrator** (full access)
     - **BTP Manager** (manager access)
     - **BTP Salesperson** (sales access)
     - **BTP Non-Sales** (limited access)
  6. **Save** and **logout/login**

**Cause 3: Menu Cache**
- **Solution**:
  1. **Logout** completely
  2. **Clear browser cache** (Ctrl+Shift+Delete)
  3. **Login** again
  4. If still not visible, **restart Odoo server**

---

### 21.2 "Open Leads is Empty"

**Symptoms**: 
- Open Leads menu shows no leads
- List is blank

**Possible Causes & Solutions**:

**Cause 1: No Leads Have Common Open Checked**
- **Solution**:
  1. Go to **BTP Prospecting → Leads**
  2. **Create a new lead** OR **open an existing lead**
  3. **Check "Common Open"** checkbox
  4. **Save**
  5. Go to **Open Leads** - lead should appear

**Cause 2: All Open Leads Were Taken**
- **Solution**: This is normal - if all open leads were claimed, the list will be empty. Create new open leads.

**Cause 3: Access Rights Issue**
- **Solution**: Verify your user has "BTP Salesperson" or "BTP Manager" group to view open leads.

---

### 21.3 "Assignment Rule Does Not Work"

**Symptoms**: 
- Leads are not assigned automatically
- Wrong user receives leads
- Leads remain unassigned

**Possible Causes & Solutions**:

**Cause 1: Rule Not Active**
- **Solution**:
  1. Go to **BTP Prospecting → Configuration → Assignment Rules**
  2. Open the rule
  3. **Check "Active"** checkbox
  4. **Save**

**Cause 2: Rule Priority Too Low**
- **Solution**:
  1. Check rule **Priority** (lower number = higher priority)
  2. If another rule with lower priority matches first, your rule won't execute
  3. **Lower the priority number** (e.g., change from 10 to 1) to give it higher priority

**Cause 3: Rule Criteria Don't Match**
- **Solution**:
  1. **Verify lead values match rule criteria**:
     - Geography rule: Check City, Country match
     - Client Type rule: Check partner categories match
     - Site Type rule: Check Site Type matches
  2. **Test with exact values** from rule

**Cause 4: No Users Available in Round-Robin**
- **Solution**:
  1. For Round-Robin rules, verify:
     - Sales Team has members, OR
     - "Assign To" fallback user is set
  2. Check users are not all "Unavailable" or "Overloaded"

**Cause 5: Non-Sales User Creating Lead**
- **Solution**: Non-Sales users cannot auto-assign leads. Leads they create are automatically "Common Open". This is expected behavior.

---

### 21.4 "Reminder Not Sent"

**Symptoms**: 
- Reminder date passed but no reminder sent
- Reminder count not increasing

**Possible Causes & Solutions**:

**Cause 1: Cron Job Not Running**
- **Solution**:
  1. Check Odoo logs: `/home/szymon/Documents/Odoo-BTP/odoo19/logs/odoo.log`
  2. Look for: `Job 'BTP Lead: Send Reminders' starting`
  3. If not found, **restart Odoo server**
  4. Verify cron is active: Check **Settings → Technical → Automation → Scheduled Actions**
  5. Find "BTP Lead: Send Reminders" and verify **Active** = Yes

**Cause 2: Lead Has No Assigned User**
- **Solution**: Reminders only send if lead has `user_id` set. Assign the lead to a user.

**Cause 3: Next Reminder Date in Future**
- **Solution**: Verify `next_reminder_date <= now`. Set it to a past date for testing.

**Cause 4: Lead is Converted or Inactive**
- **Solution**: Reminders don't send for converted or inactive leads. Check lead status.

---

### 21.5 "Cannot Set Reminder Date"

**Symptoms**: 
- Error: "Next reminder date is mandatory at this stage"
- Cannot save lead without reminder

**Solution**:
1. Go to **"Follow-up"** tab
2. **Set "Next Reminder Date"** to a future date/time
3. **Save** the lead

**Note**: This is expected if the current stage has "Require Reminder" enabled (see Section 4.2).

---

### 21.6 "Cannot See Other User's Leads"

**Symptoms**: 
- Salesperson cannot see peer's leads
- Manager cannot see subordinate's leads

**Possible Causes & Solutions**:

**Cause 1: Not a Manager**
- **Solution**: Only managers can see subordinate leads. Verify:
  1. User has **"BTP Manager"** group
  2. Manager hierarchy is set (user's manager field)

**Cause 2: Manager Hierarchy Not Set**
- **Solution**:
  1. Go to **Settings → Users & Companies → Users**
  2. Open subordinate user (e.g., Alice)
  3. Set **"Manager"** = Manager user (e.g., David)
  4. **Save**

**Cause 3: Different Companies**
- **Solution**: Users from different companies cannot see each other's leads (unless shared). Check:
  1. User's company assignment
  2. Lead's multi-company sharing settings

---

### 21.7 "Duplicate Detection Not Working"

**Symptoms**: 
- Duplicates not found
- "Check Duplicates" shows no results

**Solution**:
1. **Verify duplicate criteria**:
   - Same or similar Site Address
   - Same Partner/Client
   - Same Site Name
2. **Create test duplicate** with exact same values
3. **Run "Check Duplicates"** again

**Note**: Duplicate detection uses fuzzy matching. Very different addresses may not match.

---

### 21.8 "Cannot Convert Lead to Opportunity"

**Symptoms**: 
- "Convert to Opportunity" button disabled or missing
- Error when converting

**Possible Causes & Solutions**:

**Cause 1: Lead Already Converted**
- **Solution**: Check "Converted" field. If checked, lead is already converted.

**Cause 2: Missing CRM Module**
- **Solution**: Verify CRM module is installed (required dependency).

**Cause 3: Access Rights**
- **Solution**: Verify user has access to create opportunities in CRM.

---

### 21.9 "Round-Robin Not Distributing Evenly"

**Symptoms**: 
- One user receives all leads
- Distribution is uneven

**Possible Causes & Solutions**:

**Cause 1: User Weights Different**
- **Solution**: Check user round-robin weights. Users with weight=2 receive 2x more leads than weight=1.

**Cause 2: Users Unavailable/Overloaded**
- **Solution**: Check user availability settings. Unavailable users are excluded from pool.

**Cause 3: Only One User in Pool**
- **Solution**: Verify multiple users are in the sales team or available for assignment.

---

### 21.10 "Email Notifications Not Sent"

**Symptoms**: 
- Reminders sent but no email received
- Escalation sent but no email

**Possible Causes & Solutions**:

**Cause 1: User Has No Email**
- **Solution**: 
  1. Go to **Settings → Users & Companies → Users**
  2. Open user
  3. **Set Email** field
  4. **Save**

**Cause 2: Email Template Missing**
- **Solution**: Verify email templates exist:
  1. Go to **Settings → Technical → Email → Templates**
  2. Search for "BTP Lead" templates
  3. Verify they exist and are active

**Cause 3: Email Server Not Configured**
- **Solution**: Configure Odoo's outgoing mail server in **Settings → Technical → Outgoing Mail Servers**.

---

### 21.11 "Error: Field Not Found" or "External ID Not Found"

**Symptoms**: 
- Error messages about missing fields or external IDs
- Module installation errors

**Solution**:
1. **Upgrade the module**:
   - Go to **Apps**
   - Find "BTP Prospecting"
   - Click **"Upgrade"**
2. **Restart Odoo server**
3. **Clear browser cache**
4. If error persists, check Odoo logs for specific error details

---

### 21.12 "Performance Issues - Slow Loading"

**Symptoms**: 
- Leads list loads slowly
- Forms take time to open

**Possible Causes & Solutions**:

**Cause 1: Too Many Leads**
- **Solution**: Use filters to reduce list size. Consider archiving old leads.

**Cause 2: Database Issues**
- **Solution**: 
  1. Check database size
  2. Run database maintenance
  3. Check server resources (CPU, RAM)

**Cause 3: Missing Indexes**
- **Solution**: Contact administrator to verify database indexes are created.

---

### 21.13 Getting Help

If issues persist:

1. **Check Odoo Logs**: `/home/szymon/Documents/Odoo-BTP/odoo19/logs/odoo.log`
2. **Enable Debug Mode**: Settings → Activate Developer Mode → Check logs
3. **Review Error Messages**: Copy exact error message for troubleshooting
4. **Verify Module Version**: Check `__manifest__.py` for version number
5. **Check Dependencies**: Verify all required modules are installed

---

## 16) What this module does not include yet

This module only covers **Module 1**.
It does not include:
- Quotes module extensions
- Subcontractors management
- Sites management
- Invoicing or finance flows

If you want those, we can add them module by module later.

