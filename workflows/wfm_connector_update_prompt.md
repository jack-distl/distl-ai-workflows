# WFM Connector Update: Add Job Task Endpoints

## Problem
The WorkflowMax MCP connector currently only supports **global task endpoints** (`v2/tasks`), which manage account-level task templates. It does NOT support **job task endpoints** (`v2/jobs/tasks`), which manage tasks assigned to specific jobs — including setting estimated hours and assigning staff to job tasks.

This means we cannot:
- List the tasks within a specific job
- Update a job task's estimated hours or assigned staff
- Add new tasks to a job

## What Needs to Change

The WFM API has a completely separate set of endpoints for job-level tasks. These need to be added to the connector alongside the existing global task tools.

### 1. Add `get_job` includes support

The existing `get_job` tool calls `GET v2/jobs/{UUID}` but doesn't pass the `includes` query parameter. The API supports:

```
GET v2/jobs/{UUID}?includes=tasks,costs,notes,documents,staff,phases
```

Add an optional `includes` parameter (string or array) to the `get_job` tool so it can return tasks inline with the job. At minimum, support `includes=tasks`.

### 2. Add `list_job_tasks` tool

```
GET v2/jobs/tasks?job={jobUUID}&page={page}&pageSize={pageSize}
```

This lists all tasks assigned to a specific job. Each job task has its own UUID (different from the global task template UUID) and includes properties like estimated minutes, assigned staff, and label.

**Parameters:**
- `job` (string, required) — The UUID of the job
- `page` (number, optional) — Page number for pagination
- `pageSize` (number, optional) — Results per page

### 3. Add `update_job_task` tool

```
PUT v2/jobs/tasks/{jobTaskUUID}
```

This updates an existing task within a job. This is the critical endpoint — it sets estimated hours and assigns staff to a job task.

**URL parameter:**
- `jobTaskUUID` (string, required) — The UUID of the job task (NOT the global task UUID)

**Body parameters (all optional, send only what you want to change):**
- `estimatedMinutes` (number) — Estimated time in minutes
- `assignedStaffId` (string) — UUID of the staff member to assign
- Any other fields the API supports (check the API explorer for the full schema)

**Important:** This endpoint uses `v2/jobs/tasks/{UUID}`, NOT `v2/tasks/{UUID}`. The existing `update_task` tool calls the wrong path for job-level updates.

### 4. Add `create_job_task` tool

```
POST v2/jobs/{identifier}/tasks
```

This adds a task to a job.

**URL parameter:**
- `identifier` (string, required) — The job UUID or job number

**Body parameters:**
- `taskUUID` (string, required) — The UUID of the global task template to add (e.g. the "Digital Marketing" template UUID)
- `estimatedMinutes` (number, optional) — Estimated time in minutes
- `assignedStaffId` (string, optional) — UUID of the staff member to assign
- `label` (string, optional) — Label for the task variant (e.g. "Account Manager", "SEO Specialist")
- Other fields as supported by the API

### 5. Add `delete_job_task` tool (optional)

```
DELETE v2/jobs/tasks/{jobTaskUUID}
```

Removes a task from a job.

## How the Existing Tools Map

| Current Tool | API Path | Scope | Keep? |
|-------------|----------|-------|-------|
| `list_tasks` | `GET v2/tasks` | Global templates | Yes |
| `get_task` | `GET v2/tasks/{UUID}` | Global templates | Yes |
| `create_task` | `POST v2/tasks` | Global templates | Yes |
| `update_task` | `PUT v2/tasks/{UUID}` | Global templates | Yes |
| `delete_task` | `DELETE v2/tasks/{UUID}` | Global templates | Yes |

| New Tool | API Path | Scope |
|----------|----------|-------|
| `list_job_tasks` | `GET v2/jobs/tasks` | Tasks within a job |
| `update_job_task` | `PUT v2/jobs/tasks/{UUID}` | Update job task |
| `create_job_task` | `POST v2/jobs/{id}/tasks` | Add task to job |
| `delete_job_task` | `DELETE v2/jobs/tasks/{UUID}` | Remove from job |

### 6. Fix `create_job` tool

The existing `create_job` tool has two issues:

**a) Field name mapping bug:** The tool sends `name` and `client_id` but the WFM API expects `jobname` and `clientuuid`. The connector needs to map these correctly.

**b) Missing required fields:** The API requires `priority` (string, e.g. "Normal") and `statusuuid` (string, the job status UUID). These are not exposed as parameters. Either:
- Add them as optional parameters with sensible defaults ("Normal" and the "In Progress" status UUID `9bef861f-0d89-4151-88ff-99fc9767277d`)
- Or add a `template_id` lookup so templates can provide defaults

**c) Template support:** The tool accepts `template_id` but there's no `list_templates` endpoint to discover available templates. Add a `list_job_templates` tool if the API supports it (`GET v2/jobs/templates` or similar).

Without these fixes, jobs cannot be created via the API — they must be created manually in WFM.

---

## Testing

After adding the endpoints, test with this known job:

**Amped Digital — Digital Marketing Retainer March 2026**
- Job UUID: `a1308747-aa51-4cd6-9aaf-4cfd87108b6c`
- Job Number: `J012821`

1. Call `list_job_tasks` with `job=a1308747-aa51-4cd6-9aaf-4cfd87108b6c` — should return 5 tasks (Account Manager, SEO Specialist, Google Ads Specialist, Paid Media Specialist, Social Media Specialist)
2. Take one of the returned job task UUIDs and call `update_job_task` with `estimatedMinutes: 780` — should update the estimated time to 13 hours
3. Call `get_job` with `includes=tasks` — should return the job with tasks included in the response

## Reference

- API Base URL: `https://api.workflowmax.com`
- Auth: OAuth 2.0 (already handled by the connector)
- All requests need the `Authorization: Bearer {token}` header and organisation ID (already handled)
- Rate limit: 60 requests per minute per client-org pair
- Full API docs: WorkflowMax Developer Portal
