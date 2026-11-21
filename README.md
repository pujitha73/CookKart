# CookKart

CookKart is a planned full-stack grocery shopping and recipe discovery application. This repository is currently in **Phase 0: Architecture, Project Foundation and Development Documentation**. Customer-facing application features, database migrations, seed data, and production integrations are not implemented yet.

## Approved Product Scope (Planned)

### Primary customer sections
1. **Shop** — browse and purchase grocery and food products.
2. **Explore Recipes** — browse recipes by cuisine, collection, and meal type.
3. **My Kitchen** — manage personal pantry information and saved recipes.

### Additional customer features
4. **What Can I Cook Today?** — recommend recipes using ingredients available in the user's kitchen.
5. **Smart Recipe-to-Cart** — identify missing recipe ingredients and add corresponding grocery products to the shopping cart.

### Other customer functionality
- Authentication
- Search
- Cart
- Wishlist
- Profile
- Order history

### Admin access
A database-backed admin console is available to explicitly authorized accounts (see "Phase 10 — Administrator access" below). Sales analytics and fabricated administrative data remain out of scope.

## Technology Stack (Approved)

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- React Router

### Backend
- Python 3.12.7
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Database and Authentication
- Supabase PostgreSQL
- Supabase Auth

### Development
- Git
- Python virtual environment
- npm
- Environment variables

## Repository Structure

```text
CookKart/
  frontend/
    src/
      assets/
      components/
      layouts/
      pages/
      features/
      hooks/
      services/
      types/
      utils/
    public/
  backend/
    app/
      api/
      core/
      models/
      schemas/
      services/
      repositories/
      database/
      utils/
    migrations/
    tests/
  docs/
  .gitignore
  .env.example
  README.md
  PROJECT_SPEC.md
  ARCHITECTURE.md
  AGENTS.md
```

## Prerequisites

- **Node.js** and **npm** (verified in Phase 0 environment: Node v24.13.0, npm 11.6.2)
- **Python 3.12.7** (required for backend development)
- **Git** (verified: 2.54.0)
- **Supabase project** (PostgreSQL + Auth) — credentials to be configured later; not required for Phase 0 scaffolding

## Setup Instructions (Phase 0 foundation)

> No application dependencies are installed and no database migrations are run in Phase 0. Configure credentials only when proceeding to implementation phases.

### 1. Clone/open repository
```powershell
cd D:\CookKart
```

### 2. Backend virtual environment (Python 3.12.7)
A virtual environment scaffold can be created at `backend/.venv` using Python 3.12:
```powershell
py -3.12 -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
python --version  # should report Python 3.12.7
```

Planned backend dependencies (to be installed in a later phase): FastAPI, Pydantic, SQLAlchemy, Alembic, and related tooling as approved.

### 3. Frontend setup (planned)
When Phase 1 begins, initialize/install frontend dependencies in `frontend/` using npm and the approved stack (React, TypeScript, Vite, Tailwind CSS, React Router).

### 4. Environment variables
- Copy placeholders from `.env.example` into appropriate files (e.g., `backend/.env`, `frontend/.env`) when needed.
- **Never commit `.env` files or real credentials.**
- **Never place Supabase service-role keys or database credentials in frontend code.**

## Development Commands (Planned)

These commands are placeholders for future phases once dependencies are installed:

### Backend (FastAPI)
```powershell
# from repository root, with backend venv activated
uvicorn app.main:app --reload --app-dir backend
```

### Frontend (Vite)
```powershell
cd frontend
npm run dev
```

### Tests (planned)
```powershell
# backend
pytest backend/tests

# frontend
npm test
```

## Documentation
- [`PROJECT_SPEC.md`](PROJECT_SPEC.md) — approved scope, exclusions, design direction, recipe catalogue, and technology decisions
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — system architecture, database design, auth, API conventions, media, and security
- [`AGENTS.md`](AGENTS.md) — persistent instructions for future development in this repository

## Phase 0 Status
- Project structure scaffolded (frontend/backend/docs)
- Architecture and requirements documented
- No customer-facing UI, auth flows, seed data, or migrations implemented
- Supabase credentials not configured in application; manual configuration required before database/auth integration

## Phase 10 — Administrator access

Administrator status is stored in `public.profiles.is_admin` (boolean, `NOT NULL`, default `false`). No account is promoted automatically, and there is no hardcoded admin password. The frontend never sends or trusts a role: every admin request re-checks the database flag using the backend's privileged connection. Normal customers receive `403` from every admin endpoint.

### Configure the first administrator (manual, privileged SQL only)

1. Apply migrations: `alembic upgrade head` from `backend/` (revision `0003_profile_is_admin` adds the flag).
2. Have the intended administrator sign up through the normal CookKart flow, or identify an existing Supabase Auth user. Use an individual account with its own password — never a shared credential.
3. In a **privileged SQL session only** (Supabase SQL editor or the backend database role; never the browser/PostgREST), grant the flag:

```sql
-- Replace with the UUID from auth.users for the account you trust.
INSERT INTO public.profiles (id, display_name, is_admin)
VALUES ('<ADMIN_USER_ID>', 'CookKart Admin', true)
ON CONFLICT (id) DO UPDATE SET is_admin = true;
```

4. Sign out and back in. The Admin link appears only after `GET /api/admin/me` confirms the database flag.

To revoke access: `UPDATE public.profiles SET is_admin = false WHERE id = '<ADMIN_USER_ID>';`

### Why customers cannot promote themselves

Migration `0003_profile_is_admin` revokes table-level `INSERT`/`UPDATE` on `profiles` from `anon` and `authenticated`, replacing them with column-scoped grants: `INSERT (id, display_name, avatar_url)` and `UPDATE (display_name, avatar_url)`. The `is_admin` column is deliberately excluded, so it cannot be changed through the Supabase client or PostgREST. Only the privileged backend connection can modify it.

### Admin API endpoints

All require a valid Supabase Bearer token **and** a database-confirmed admin profile.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/admin/me` | Confirm admin access for the frontend |
| GET | `/api/admin/dashboard` | Real order-status and catalogue counts |
| GET | `/api/admin/orders` | List/search/filter orders (`search`, `status`, `page`, `page_size`) |
| GET | `/api/admin/orders/{id}` | Order detail with delivery info, items and totals |
| PATCH | `/api/admin/orders/{id}/status` | Validate and apply `placed→confirmed`, `placed→cancelled`, `confirmed→cancelled` |
| GET | `/api/admin/products` | Browse/search products including unavailable ones |
| PATCH | `/api/admin/products/{id}/availability` | Enable or disable a product only |

Order-item snapshots and original order totals are never rewritten. Product prices are never editable from the admin API.
