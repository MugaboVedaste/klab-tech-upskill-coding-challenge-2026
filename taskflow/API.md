# TaskFlow REST API

A token-authenticated JSON API for external clients (mobile apps, scripts,
Postman, other services). It sits alongside — and is completely separate
from — the server-rendered web UI at `/accounts/`, `/dashboard/`, and
`/tasks/`. The web UI uses browser sessions; this API uses auth tokens and
is meant to be consumed by non-browser clients.

Base URL: `http://<host>/api/`

All requests and responses are JSON (`Content-Type: application/json`),
except the token endpoint which also accepts form-encoded data.

## Roles

Every account has a role that determines what it can do:

| Role | Can |
|---|---|
| **Manager** | Create employees, create/edit/delete tasks, assign tasks to their own employees, review completed tasks |
| **Employee** | View tasks assigned to them, move a task through its status workflow |
| **Superuser** | Site administration only (Django admin) — no manager/employee role, not part of this API |

A manager only ever sees/manages the employees and tasks they own. An
employee only ever sees tasks assigned to them. Trying to access another
account's data returns `404 Not Found` (not `403`), so the API never
reveals that the resource exists.

---

## 1. Authentication

### Register (manager)

```
POST /api/auth/register/
```

No auth required. Self-service manager sign-up — same rules as the web
UI's `/accounts/register/`: the account is created **inactive** and
needs an administrator to approve it (via Django admin) before it can
log in. `department` is optional.

```json
{
  "username": "mugabo",
  "first_name": "Mugabo",
  "last_name": "Vedaste",
  "email": "mugabo@example.com",
  "password": "secret",
  "department": "Engineering"
}
```

**Response `201`**

```json
{
  "detail": "Registration submitted. An administrator must approve your account before you can log in.",
  "username": "mugabo"
}
```

`400` if the username/email is taken or a required field is missing.

There's no self-registration for employees — a manager creates those
via `POST /api/employees/` (see [Employees](#2-employees) below) or the
web UI, and they're immediately active.

### Login

```
POST /api/auth/login/
```

Form-encoded or JSON body:

```json
{ "username": "mugabo", "password": "secret" }
```

**Response `200`**

```json
{ "token": "09686e187263666727d5af0eb7c05df4f18289fc" }
```

`400` if the credentials are wrong, or the account isn't active yet
(pending manager approval, or paused). `POST /api/auth/token/` is an
alias of this same endpoint (standard DRF naming), kept for clients
that expect it.

### Using the token

Send it on every subsequent request:

```
Authorization: Bearer 09686e187263666727d5af0eb7c05df4f18289fc
```

Requests with no token, or a bad one, get `401 Unauthorized`. Requests
from an authenticated account that isn't allowed to perform that action
(e.g. an employee trying to create a task) get `403 Forbidden`.

---

## 2. Employees

Manager-only. An employee record is a `User` with `role=employee`.

### List your employees

```
GET /api/employees/
```

**Response `200`**

```json
[
  {
    "id": 34,
    "username": "sabin",
    "first_name": "Sabin",
    "last_name": "K",
    "full_name": "Sabin K",
    "email": "sabin@example.com",
    "department": "Sales",
    "is_active": true
  }
]
```

### Get one employee

```
GET /api/employees/{id}/
```

`404` if the employee doesn't exist or isn't yours.

### Create an employee

```
POST /api/employees/
```

```json
{
  "username": "newhire",
  "first_name": "New",
  "last_name": "Hire",
  "email": "newhire@example.com",
  "password": "temporary-password"
}
```

The new account is automatically assigned to you as manager and inherits
your `department`. **Response `201`** with the created employee (same
shape as the list above). `400` if the username/email is taken or a
required field is missing.

### Pause / resume an employee

```
POST /api/employees/{id}/pause/
POST /api/employees/{id}/resume/
```

No body needed. Pausing sets `is_active=false`, which also blocks that
account from logging in. You can't pause your own account. **Response
`200`** with the updated employee. `404` if not one of your employees.

---

## 3. Tasks

A task has a `status` that only moves forward through a fixed workflow —
see [Task status workflow](#task-status-workflow) below. `status` is
read-only on create/update; it only changes via the `status/` and
`review/` actions described below.

| Field | Type | Notes |
|---|---|---|
| `id` | int | |
| `title` | string | required |
| `description` | string | optional |
| `status` | string | `pending` / `in_progress` / `done` / `reviewed` / `rejected` — read-only |
| `status_display` | string | human-readable status |
| `priority` | string | `low` / `medium` / `high` |
| `priority_display` | string | human-readable priority |
| `assigned_to` | object | `{id, username, full_name}` |
| `created_by` | object | `{id, username, full_name}` |
| `created_at` / `updated_at` | datetime | ISO 8601, UTC |

### List tasks

```
GET /api/tasks/
GET /api/tasks/?status=in_progress
```

- **Manager**: returns tasks they created.
- **Employee**: returns tasks assigned to them.
- `status` query param filters by any of the five status values.

**Response `200`**

```json
[
  {
    "id": 12,
    "title": "Fix login bug",
    "description": "",
    "status": "in_progress",
    "status_display": "In Progress",
    "priority": "high",
    "priority_display": "High",
    "assigned_to": { "id": 34, "username": "sabin", "full_name": "Sabin K" },
    "created_by": { "id": 2, "username": "mugabo", "full_name": "Mugabo V" },
    "created_at": "2026-09-17T20:17:43.011005Z",
    "updated_at": "2026-09-17T20:46:19.066209Z"
  }
]
```

### Get one task

```
GET /api/tasks/{id}/
```

Scoped the same way as the list. `404` if it's not yours.

### Create a task

```
POST /api/tasks/
```

Manager only.

```json
{
  "title": "Write onboarding doc",
  "description": "Covers day-1 setup",
  "priority": "medium",
  "assigned_to": 34
}
```

`assigned_to` must be one of **your own active employees** — anything
else is rejected with `400`. New tasks always start at `status=pending`.
**Response `201`** with the created task.

### Update a task

```
PUT /api/tasks/{id}/
PATCH /api/tasks/{id}/
```

Manager only, and only for tasks they created. Editable fields: `title`,
`description`, `priority`, `assigned_to` (same active-employee
restriction as create). `status` cannot be changed here — use
`status/` or `review/`.

`PUT` requires **all** editable fields (it's a full replace):

```json
{
  "title": "Write onboarding doc",
  "description": "Covers day-1 setup, updated for the new laptop policy",
  "priority": "high",
  "assigned_to": 34
}
```

`PATCH` allows a partial update — send only the fields you're changing:

```json
{ "priority": "high" }
```

**Response `200`** with the updated task.

### Delete a task

```
DELETE /api/tasks/{id}/
```

Manager only, and only for tasks they created. **Response `204`**.

### Update task status (employee)

```
POST /api/tasks/{id}/status/
```

Employee only, and only for tasks assigned to them.

```json
{ "status": "in_progress" }
```

Only the transitions in the table below are accepted; anything else
returns `400 {"detail": "Invalid status transition."}`.

| Current status | Allowed next status |
|---|---|
| `pending` | `in_progress` |
| `in_progress` | `done` |
| `rejected` | `in_progress` or `done` |

**Response `200`** with the updated task.

### Review a task (manager)

```
POST /api/tasks/{id}/review/
```

Manager only, and only for tasks they created. The task must currently
be `done`.

```json
{ "decision": "reviewed" }
```

or

```json
{ "decision": "rejected" }
```

`400` if the task isn't `done` yet, or `decision` isn't one of those two
values. **Response `200`** with the updated task.

---

## Task status workflow

```
pending ──▶ in_progress ──▶ done ──▶ reviewed   (terminal)
                 ▲             │
                 │             ▼
                 └────────  rejected
                    (employee can also go straight
                     from rejected back to done)
```

1. Manager creates a task → `pending`.
2. Employee starts it → `in_progress`.
3. Employee finishes it → `done`.
4. Manager reviews: `reviewed` (accepted, terminal) or `rejected` (needs
   rework).
5. If `rejected`, the employee fixes the issue and marks it `done` again
   (optionally passing through `in_progress` first) — back to step 4.

---

## Error format

Validation errors follow DRF's default shape — a JSON object mapping
field name to a list of error messages:

```json
{ "title": ["This field is required."] }
```

Action-specific errors (invalid status transition, reviewing a task
that isn't done yet, etc.) use `{"detail": "..."}`.

| Status | Meaning |
|---|---|
| `400` | Validation error / invalid state transition |
| `401` | Missing or invalid auth token |
| `403` | Authenticated, but not allowed to perform this action (wrong role) |
| `404` | Not found, or not yours |
