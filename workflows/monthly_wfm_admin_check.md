# Monthly WorkflowMax Admin Check

## Objective
On the 1st of each month, audit all WorkflowMax jobs completed in the previous calendar month to identify time tracking hygiene issues before invoicing or reporting is affected. Specifically: tasks where time has been logged but no staff member is assigned, and jobs where multiple unassigned tasks both carry time (wrong attribution risk).

## When to Run
- **Trigger:** 1st of each calendar month
- **Covers:** Previous full calendar month (calculated automatically from today's date)

## Prerequisites
- MCP connector authenticated: **WorkflowMax**

---

## Process Overview

```
Calculate previous month date range (Step 1)
  |
  v
list_jobs with reverse pagination (Step 2)
  |-- Start from last page, work backward
  |-- Filter by completedDate, stop when past target month
  |
  v
get_job with includes=tasks for every job UUID (Step 3)
  |-- Run in parallel batches of ~10
  |
  v
Apply Check 1 + Check 2 to each job (Step 4)
  |-- Check 1: actualMinutes > 0 AND staff = [] → flag task
  |-- Check 2: 2+ flagged tasks on same job → wrong attribution risk
  |
  v
Collect context for flagged jobs (Step 5)
  |
  v
Output: Section 1 + Section 2 + Section 3 + Remediation Plan
```

---

## Step 1: Determine the Date Range

Calculate the first and last day of the **previous calendar month** based on today's date.

**Example:** If today is 1 April 2026, the range is:
- Start: `2026-03-01`
- End: `2026-03-31`

The target month prefix for filtering is `2026-03`.

Do this calculation at the start of each run. Do not hardcode dates.

---

## Step 2: Get All Jobs Completed Last Month

Use **reverse pagination** to efficiently find recently completed jobs without fetching the entire job history.

### Why reverse pagination

Completed jobs in WorkflowMax are returned in ascending date order. The most recent completions are on the last pages. The `list_jobs` connector does support `completed_after` / `completed_before` parameters for client-side filtering, but these require fetching all pages of completed jobs (~100+ pages for a mature account), which triggers API rate limits (429 errors). Reverse pagination avoids this by starting from the end and only fetching the 2–4 pages that contain the target month.

### Procedure

1. **Get the last page number.** Call `list_jobs` with `status=Completed` and `page=1` and `page_size=100`. The response includes a `total` field. Calculate the last page: `lastPage = ceil(total / 100)`.

2. **Fetch the last page.** Call `list_jobs` with `status=Completed` and `page=lastPage` and `page_size=100`.

3. **Filter and check.** From the returned jobs, collect any where `completedDate` starts with the target month prefix (e.g. `2026-03`). Also check whether the page contains jobs completed **before** the target month — if so, you have reached the boundary.

4. **Page backward.** Fetch `page=lastPage - 1`, then `lastPage - 2`, etc. Continue until you reach a page where **all** jobs have a `completedDate` before the target month. At that point, stop — you have all the jobs.

5. **Collect results.** Combine all matching jobs across the fetched pages. This is your full list of job UUIDs and job numbers for the month.

**Typical volume:** Expect 50–150 completed jobs per month, usually spanning 2–4 pages near the end of the list.

---

## Step 3: Fetch Task-Level Data for Each Job

For every job UUID collected in Step 2, call `get_job` with `includes=tasks`.

This returns the full task list for each job, including:
- Task name / label
- `actualMinutes` — total time logged against the task
- `staff` — array of assigned staff members (empty array `[]` means no one is assigned)

**Run these calls in parallel batches** of approximately 10 jobs at a time. With 75+ jobs, expect 8–10 batches. Do not run all calls sequentially — that will be too slow.

---

## Step 4: Apply the Checks

For each job, loop through its tasks and apply both checks.

### Check 1 — Unassigned time

Flag a task if **both** conditions are true:
- `task.actualMinutes > 0`
- `task.staff` is empty (no assigned staff)

This means someone logged time to a task with no owner.

### Check 2 — Wrong attribution risk

After processing all tasks in a job:
- If **two or more tasks** in the same job are flagged under Check 1, additionally flag the job for wrong attribution risk

When multiple unassigned tasks in the same job both have time logged, there is a risk that a specialist logged time against the wrong slot.

---

## Step 5: Collect Context for Flagged Jobs

For each job with at least one flagged task, note:

| Field | Source |
|-------|--------|
| Job number | Job-level field |
| Client name | Job-level field |
| Flagged task name / label | Task-level field |
| Time logged on flagged task | `task.actualMinutes` ÷ 60, rounded to 2 decimal places |
| Job manager | Job-level `jobManager` field — if blank, note *(none set)* |
| Other staff on job | Staff assigned to **non-flagged** tasks on the same job — include their task name/role |

---

## Output Format

Present findings in three sections.

---

### Section 1 — Unassigned Tasks with Time

One row per flagged task:

| Job | Client | Flagged Task | Time | Job Manager | Other Staff on Job |
|-----|--------|--------------|------|-------------|-------------------|
| J012XXX | Client name | Task label | X.XX hrs | Name | Name (task), Name (task) |

- If a job has no other assigned staff at all, note *(no other tasks assigned)*
- If the flagged task is the only task on the job, note *(only task on job)*
- Convert minutes to hours: divide by 60, round to 2 decimal places

---

### Section 2 — Wrong Attribution Risk

List jobs where two or more unassigned tasks both have time logged:

| Job | Client | Unassigned Tasks with Time |
|-----|--------|---------------------------|
| J012XXX | Client name | Task A (X.XX hrs, unassigned) + Task B (X.XX hrs, unassigned) |

---

### Section 3 — Summary

- Total flagged tasks (Check 1)
- Total hours affected (sum of all unassigned time, in hours)
- Total jobs involved
- Number of jobs flagged for wrong attribution risk (Check 2)

---

## Remediation Plan

After presenting the three sections, produce a prioritised action plan. Work through flagged items in this order:

### 1. High priority — large unassigned time blocks
Any task with more than 2 hours of unassigned time should be investigated first. Based on the other staff assigned to the job, identify the likely owner and suggest reassigning the task in WorkflowMax.

**Example:** "Task: Digital Marketing – Google Ads Specialist on J012XXX (3.5 hrs, unassigned). Zachary Fitzpatrick is assigned to the Google Ads task on another job for the same client this month — likely the correct person to assign here."

### 2. Wrong attribution jobs
For jobs flagged under Check 2, review whether time was split between two unassigned slots in error. The correct fix is usually to consolidate all time onto the correct task and assign the appropriate staff member.

### 3. Fully unmanaged jobs
Jobs where there are no other assigned tasks at all have no obvious candidate for who logged the time. These cannot be resolved automatically. Raise with the job manager for investigation.

### 4. Small unassigned time entries
Tasks with under 30 minutes of unassigned time may be minor logging errors (e.g. a timer left running). Still include these but treat as lower priority.

For each item, suggest the likely owner based on other staff on the job where possible. If no suggestion can be made, state that explicitly.

---

## Edge Cases and Notes

1. **Date calculation:** Always derive the date range programmatically from today's date. If run on a day other than the 1st (e.g. manually triggered mid-month), still use the previous full calendar month.

2. **Pagination:** Use reverse pagination as described in Step 2. Do not use `completed_after` / `completed_before` parameters — they fetch all completed job pages and trigger 429 rate limits on accounts with large job histories (10,000+ completed jobs). Reverse pagination typically needs only 2–4 page fetches.

3. **Parallel batching:** With 75+ jobs, running `get_job` calls sequentially is too slow. Use parallel batches of ~10. If the connector enforces rate limits, reduce batch size and add a brief pause between batches.

4. **Job number appearing twice in results:** This means two separate tasks on the same job are flagged. It is not a duplicate — list both rows in Section 1.

5. **Empty job manager field:** Some older jobs have no `jobManager` set. Note *(none set)* and include these jobs in the remediation plan as they need account-level cleanup regardless of the time tracking issue.

6. **Batch completions at month end:** Most retainer jobs are batch-closed at the end of the month, so expect a cluster of completions in the last 3–5 days of the month. This is normal — it does not indicate a problem with the data.

7. **Scope of this check:** This audit covers time tracking hygiene only. It does not audit billing amounts, job budgets, invoiced values, or job statuses beyond completion.

8. **Staff array format:** The `staff` field is an array. An empty array `[]` means no one is assigned. A task with one or more entries in `staff` is considered assigned and should **not** be flagged, regardless of how much time is logged.

---

## Connected Systems

| System | Access Method | Purpose |
|--------|-------------|---------|
| WorkflowMax | MCP connector | Read completed jobs and task-level time data |
