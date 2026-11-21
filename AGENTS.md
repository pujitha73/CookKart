# AGENTS.md — Persistent Development Instructions for CookKart

These instructions apply to all future development work in this repository unless explicitly superseded by an approved updated specification.

## 1. Inspect Before Modifying
- Verify the working directory and inspect existing files/folders before making changes.
- Preserve existing files and working code; do not assume dependencies or configurations exist.
- Check relevant tool/runtime availability before relying on them.

## 2. Follow Approved Scope and Specification
- Follow `PROJECT_SPEC.md`, `ARCHITECTURE.md`, and approved phase boundaries.
- Do not introduce additional major features without approval.
- Do not build admin dashboard, sales analytics, or fabricated administrative data (an honest placeholder entry point only, if specified).

## 3. Architecture and Code Organization
- Maintain frontend/backend separation (`frontend/`, `backend/`).
- Keep UI components, business logic, API routes, and database access separate.
- Follow the established project structure and document any technically justified deviations.
- Keep changes consistent with surrounding code style, naming, and patterns.

## 4. Dependencies and Tooling
- Use the approved technology stack (React, TypeScript, Vite, Tailwind CSS, React Router; Python 3.12.7, FastAPI, Pydantic, SQLAlchemy, Alembic; Supabase PostgreSQL/Auth; Git, npm, venv, env vars).
- Avoid unnecessary frameworks or dependencies.
- Use Python 3.12.7 for backend development.

## 5. Security and Secrets
- Never expose credentials in code, logs, documentation, or tool output.
- Never commit `.env` files.
- Never place Supabase service-role keys or database credentials in frontend code.
- Keep frontend and backend environment variables separate where appropriate.
- Plan and enforce secure authentication and user data isolation (including RLS for user-owned data).

## 6. Data, Media, and Content Integrity
- Use Supabase Auth for identity/authentication; do not implement a separate password system.
- Do not generate fake customer data, fake orders, sales records, or unapproved seed data.
- Do not invent or generate unverified external URLs for images/videos.
- Store media references (external optimized image URLs, YouTube IDs/validated URLs) rather than local media files.

## 7. Testing and Verification
- Write tests for implemented functionality.
- Verify changes with relevant checks/commands and report actual results.
- Never claim unverified functionality is complete.

## 8. Change Discipline
- Avoid unrelated file rewrites.
- Ask for clarification instead of inventing requirements or making unsupported assumptions.
- When issues/blockers are found (e.g., missing required runtime/version), stop and report them clearly.