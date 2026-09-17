# TaskFlow

A task management system built for the kLab Tech Upskill Program coding
challenge. Managers create employee accounts, assign them tasks, and
review completed work; employees work through their assigned tasks and
resubmit anything that gets sent back. Server-rendered web UI plus a
separate token-authenticated REST API for external clients.

## Features

- **Role-based accounts** — Manager, Employee, and Superuser (site admin
  only, no business role). Public manager self-registration requires
  admin approval before the account can log in.
- **Employee management** — a manager creates employee accounts, which
  are scoped to them by direct ownership (not just a shared department
  name — two managers in the same department never see each other's
  employees). Managers can pause/resume an employee's access.
- **Task lifecycle** — a task moves through a fixed workflow:

  ```
  pending → in_progress → done → reviewed   (terminal)
                ▲            │
                │            ▼
                └────────  rejected
  ```

  The manager creates and assigns tasks; the employee moves a task from
  `pending` to `in_progress` to `done`; the manager then reviews it as
  `reviewed` (accepted) or `rejected` (needs rework — the employee fixes
  it and marks it `done` again). Every transition is validated — you
  can't skip straight to `done`, and only the task's owner/assignee can
  act on it.
- **Manager dashboard** — task counts by status and a 7-day trend line
  chart (tasks created vs. reviewed), drawn as plain inline SVG — no
  external charting library.
- **REST API** (`/api/`) — see [`taskflow/API.md`](taskflow/API.md) for
  full documentation. Bearer-token authentication, register/login,
  employee management, and full task CRUD + workflow actions, all
  scoped identically to the web UI.

## Tech stack

| | |
|---|---|
| Backend | Django 5.2, Django REST Framework |
| Database | SQLite (zero-config; swap `DATABASES` in `config/settings.py` for Postgres/MySQL in production) |
| Frontend | Server-rendered Django templates, plain CSS, a little vanilla JS (no build step, no framework) |
| Auth | Django sessions (web UI) / Bearer tokens via DRF's token auth (API) |

## Project structure

```
taskflow/
├── accounts/     # custom User model (role, department, manager FK), auth views, employee management
├── tasks/        # Task model, status workflow, task views, shared transition rules
├── dashboard/    # role-aware landing page (manager stats/trend vs. employee task list)
├── config/       # settings, root urls, REST API router (config/api_urls.py)
├── templates/    # HTML templates for the web UI
├── static/       # CSS/JS
├── API.md        # REST API reference
└── requirements.txt
```

## Setup — running it on a new machine

Prerequisites: **Python 3.11+** (developed on 3.13).

```bash
# 1. Clone and enter the project
git clone <this-repo-url>
cd klab-tech-upskill-coding-challenge-2026/taskflow

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up the database (SQLite — no separate install/service needed)
python manage.py migrate

# 5. Create an admin account (to approve manager registrations, use /admin/)
python manage.py createsuperuser

# 6. Run it
python manage.py runserver
```

Then visit:

- `http://127.0.0.1:8000/accounts/register/` — register as a manager (needs approval from `/admin/` before you can log in)
- `http://127.0.0.1:8000/accounts/login/` — log in
- `http://127.0.0.1:8000/admin/` — Django admin (approve managers, inspect data)
- `http://127.0.0.1:8000/api/` — REST API root; see [`taskflow/API.md`](taskflow/API.md)

### Environment variables (optional)

The app runs out of the box with dev-safe defaults. For anything beyond
local development, set:

| Variable | Purpose | Default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django's cryptographic signing key | a fallback dev-only key |
| `DJANGO_DEBUG` | `True`/`False` | `True` |
| `DJANGO_ALLOWED_HOSTS` | comma-separated hostnames | empty |

## Technical decisions

- **Ownership over shared labels.** Employees are linked to their
  manager via a direct foreign key (`User.manager`), not just a
  `department` string — so scoping stays correct even when two managers
  share a department name.
- **One workflow, enforced in one place.** The allowed status
  transitions (`tasks/transitions.py`) are imported by both the HTML
  views and the REST API, so the two surfaces can never drift apart on
  what counts as a valid move.
- **404, not 403, on cross-account access.** Trying to view/act on
  another manager's or employee's data returns "not found" rather than
  "forbidden," so the API/UI never confirms that the resource exists.
- **Superusers aren't managers or employees.** `role` is left blank for
  superuser accounts, and they're redirected to `/admin/` instead of
  being funneled into a business-role dashboard.
