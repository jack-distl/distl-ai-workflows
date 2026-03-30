# Monthly WFM Retainer Setup

## Objective
At the start of each month, populate the estimated hours and assign staff to the WorkflowMax (WFM) recurring retainer jobs for all active digital marketing clients. This ensures every active client's monthly job has the correct hours and the right people assigned before work begins.

## When to Run
- **Trigger:** 2nd of each calendar month
- **Schedule:** Will be scheduled to run automatically

## Prerequisites
- MCP connectors authenticated: **Monday.com** and **WorkflowMax**
- Recurring jobs already created in WFM for the month (named "Digital Marketing Retainer [Month Year]", e.g. "Digital Marketing Retainer April 2026")

---

## Process Overview

```
Monday: DM Client Health Check (active clients + hours)
  +
Monday: Specialist boards (who does the work)
  =
WFM: Update retainer job tasks with hours + assigned staff
```

---

## Step 1: Get Active Clients, Their Hours, and Retainer Status

**Source:** Monday.com - DM Client Health Check board (`208440216`)

**This board is the bible.** It is the single source of truth for:
- Whether a client should have a WFM job populated (based on Status + Retainer Status)
- How many hours should be allocated to each service

**Filter:** `status2` column = "Active" (label id `1`)

**Columns to retrieve:**

| Column ID | Column Title | Purpose |
|-----------|-------------|---------|
| `name` | Client Name | Match to WFM job client |
| `status` | RETAINER STATUS | Determines whether to proceed (see decision logic below) |
| `status2` | Status | Active/Inactive/Paused filter |
| `people` | AM | Account Manager - gets AM hours in WFM |
| `formula_18` | AM Hours | Hours for the "Digital Marketing - Account Manager" task |
| `dup__of_am_hours` | SEO Hours | Hours for the "Digital Marketing - SEO Specialist" task |
| `dup__of_seo_hours` | Google Ads Hours | Hours for the "Digital Marketing - Google Ads Specialist" task |
| `formula` | Paid Media Hours | Hours for the "Digital Marketing - Paid Media Specialist" task |
| `formula4` | Organic Social Hours | Hours for the "Digital Marketing - Organic Social Specialist" task |

**Note:** The hours columns are formula fields calculated from retainer values. They return whole numbers (already rounded).

**Pagination:** The board has ~219 items total. Use pagination (50 limit per page) and filter for Active status to get only relevant clients.

---

### Retainer Status Decision Logic

The `status` column (RETAINER STATUS) determines whether to proceed with populating the WFM job for each client. Since this workflow runs on the 2nd of the month, most clients will already be set to INVOICED by then.

**Proceed — populate the WFM job:**
| Retainer Status | Action |
|----------------|--------|
| `INVOICED` | Proceed. This is the most common status on the 2nd. |
| `APPROVED` | Proceed. Retainer is approved and ready to go. |
| `INTERNAL` | Proceed. Internal client, still needs WFM hours. |
| `INVOICED IN ADVANCE` | Proceed. Already invoiced, work should be planned. |
| `APPROVED - $ HAS CHANGED` | Proceed. Approved but dollar value changed — the hours formulas on the board will already reflect the new value, so use the current hours as-is. |

**Do not proceed — flag for review:**
| Retainer Status | Action |
|----------------|--------|
| `PAUSED` | Skip. Retainer is paused, no WFM job needed. |
| `HOLD` | Skip. Retainer is on hold. |
| `CANCELLED` | Skip. Client has cancelled. |
| `NOT TO BE INVOICED` | Skip. No billable retainer. |
| `COMMENCE NEXT MONTH` | Skip. Client starts next month, not this one. |

**Requires manual review:**
| Retainer Status | Action |
|----------------|--------|
| `SEE NOTES` | Do not auto-populate. Read the Updates on the Monday item for context and flag to user with the update content. |
| `New` | Do not auto-populate. New client — may not have a WFM job yet. Flag to user. |
| *(blank/empty)* | Do not auto-populate. No retainer status set. Flag to user. |

**When flagging for review**, include the client name, AM, retainer status, total hours, and any relevant Updates from the Monday item so the user has enough context to decide.

---

## Step 2: Look Up Specialists for Each Client

The Account Manager (AM) is already on the DM Client Health Check board in the `people` column. They always get assigned the AM Hours task as the **job manager**.

**The specialist boards are the bible for who gets assigned.** For specialist roles, look up each client by name on the corresponding specialist board:

| Service | Monday Board | Board ID | Specialist Column |
|---------|-------------|----------|-------------------|
| SEO | SEO Project Management | `1873344869` | `people` (titled "SEO") |
| Google Ads | Google Ads - Ongoing Campaigns | `3518097531` | `dup__of_pl` (titled "Specialist") |
| Paid Media | Paid Media - Ongoing Campaigns | `3565835048` | `dup__of_pl` (titled "Specialist") |
| Organic Social | Organic Socials - Ongoing Clients | `3484029825` | `dup__of_person` (titled "Specialist") |

**How to match:** Search each specialist board for the client name. The client should appear as an item in the "Active" group on each board they have hours for.

**Edge case:** If a client has 0 hours for a service (e.g. `formula4` = 0 for Organic Social), skip the specialist lookup for that service - there's no task to assign.

---

## Step 3: Match to WFM Jobs

**In WorkflowMax**, each active client should already have a recurring job created for the current month.

**Job naming convention:** `Digital Marketing Retainer [Month Year]`
- Example: `Digital Marketing Retainer April 2026`

**How to find the job:**
1. Use `list_jobs` with `status: "Active"` to get all active jobs
2. Filter for jobs where the name contains "Digital Marketing Retainer" AND the current month/year
3. Match the WFM job's client name to the Monday board client name

**Important:** Client names must match between Monday and WFM. If a client name doesn't match exactly, flag it for manual review.

---

## Step 4: Update Tasks Within Each Job

Each WFM retainer job contains the same set of standard tasks. For each task, set the **estimated hours** and **assign the staff member**.

**Task-to-data mapping:**

| WFM Task Name | Hours Source (Monday Column) | Staff Source |
|---------------|------------------------------|-------------|
| Digital Marketing - Account Manager | `formula_18` (AM Hours) | AM from `people` column on DM Client Health Check |
| Digital Marketing - SEO Specialist | `dup__of_am_hours` (SEO Hours) | SEO specialist from SEO Project Management board |
| Digital Marketing - Google Ads Specialist | `dup__of_seo_hours` (Google Ads Hours) | Specialist from Google Ads - Ongoing Campaigns board |
| Digital Marketing - Paid Media Specialist | `formula` (Paid Media Hours) | Specialist from Paid Media - Ongoing Campaigns board |
| Digital Marketing - Organic Social Specialist | `formula4` (Organic Social Hours) | Specialist from Organic Socials - Ongoing Clients board |

**For each task:**
1. Convert hours to minutes (hours x 60) for the `estimated_minutes` field
2. Look up the staff member's WFM staff ID (match Monday person name to WFM `list_staff` results)
3. Update the task with estimated time and assigned staff using `create_task` or update endpoint

**Skip condition:** If hours = 0 for a service, do not assign anyone to that task (leave it empty or skip it).

---

## Step 5: Validation and Reporting

After processing all clients, produce a summary:

**Success report:**
- Client name
- Job ID in WFM
- Hours assigned per task
- Staff assigned per task

**Exceptions to flag:**
- Client active on Monday but no matching WFM job found
- Client name mismatch between Monday and WFM
- Staff member on Monday not found in WFM staff list
- Hours = 0 across all services (client is "active" but has no retainer value)

---

## Staff ID Mapping

Before running the main loop, pull the full staff list from WFM using `list_staff`. Build a lookup table mapping staff names to WFM staff IDs. This avoids repeated API calls.

Monday stores people as names (e.g. "Jack Headford"). WFM has its own staff IDs. The mapping must be done by matching names.

---

## Data Flow Diagram

```
DM Client Health Check (Monday 208440216)
  |
  |-- Filter: status2 = Active
  |-- Get: client name, AM, RETAINER STATUS, AM hrs, SEO hrs, GAds hrs, PM hrs, OS hrs
  |
  v
Retainer Status Check
  |-- INVOICED / APPROVED / INTERNAL / INVOICED IN ADVANCE / APPROVED - $ HAS CHANGED --> Proceed
  |-- PAUSED / HOLD / CANCELLED / NOT TO BE INVOICED / COMMENCE NEXT MONTH --> Skip
  |-- SEE NOTES / New / blank --> Flag for manual review (read Updates)
  |
  v
Specialist Lookup (Monday boards — the bible for WHO)
  |-- SEO PM (1873344869) --> SEO specialist name
  |-- GAds (3518097531) --> GAds specialist name
  |-- Paid Media (3565835048) --> PM specialist name
  |-- Organic Social (3484029825) --> OS specialist name
  |
  v
Staff ID Resolution (WFM list_staff)
  |-- Map Monday names --> WFM staff IDs
  |
  v
WFM Job Matching (list_jobs)
  |-- Find "Digital Marketing Retainer [Month Year]" per client
  |
  v
WFM Task Updates
  |-- Set estimated_minutes + assigned_staff_id per task
```

---

## Example: Amped Digital (March 2026)

**Monday data:**
- AM: Jack Headford
- AM Hours: 13
- SEO Hours: 19
- Google Ads Hours: 0
- Paid Media Hours: 0
- Organic Social Hours: 0

**Specialist lookup:**
- SEO: Jakeb Munn (from SEO Project Management board)
- Others: N/A (0 hours)

**WFM job:** J012821 - Digital Marketing Retainer March 2026

**Task updates:**
| Task | Hours | Minutes | Assigned To |
|------|-------|---------|-------------|
| Digital Marketing - Account Manager | 13 | 780 | Jack Headford |
| Digital Marketing - SEO Specialist | 19 | 1140 | Jakeb Munn |
| Digital Marketing - Google Ads Specialist | 0 | 0 | (skip) |
| Digital Marketing - Paid Media Specialist | 0 | 0 | (skip) |

---

## Edge Cases and Notes

1. **New clients:** If a client was just added to Monday as Active but doesn't have a WFM recurring job yet, flag for manual setup
2. **Paused/Hold clients:** Only process clients where `status2` = Active. Ignore PAUSED, HOLD, and Inactive
3. **Retainer Status is key:** Even if `status2` = Active, always check the `status` (RETAINER STATUS) column before populating. A client can be Active but have a PAUSED, HOLD, or COMMENCE NEXT MONTH retainer status — in those cases, do not populate the WFM job. See the decision logic in Step 1.
4. **Multiple specialists:** If a specialist column has multiple people, use the first person listed
5. **Name mismatches:** Maintain awareness that client names might differ slightly between Monday and WFM (e.g. "Summit Developments" vs "Summit Developments Pty Ltd", "KinderPark / Lex Education Pty Ltd" vs "Lex Education Pty Ltd", "DoubleUP Tours" vs "Double Up"). Flag these for manual review rather than guessing
6. **EDM Retainer:** The EDM retainer value feeds into the AM Hours formula calculation but does not have its own separate task in WFM
7. **Month format:** Use full month name + 4-digit year (e.g. "April 2026", not "Apr 2026" or "04/2026")
8. **Combined retainers:** Some clients share a single WFM job across multiple Monday entries (e.g. Swivelpole AU + Swivelpole EU are combined into one WFM "Swivelpole" job). When this is the case, sum the hours from both entries before populating the WFM job.

---

## Connected Systems

| System | Access Method | Purpose |
|--------|-------------|---------|
| Monday.com | MCP connector | Read client data, hours, specialists |
| WorkflowMax | MCP connector | Update job tasks with hours and staff |
