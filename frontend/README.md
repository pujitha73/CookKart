# CookKart Frontend (Phase 1 + Phase 2)

Phase 1 implemented the frontend foundation and UI/UX shell. Phase 2 adds **customer authentication** using Supabase Auth (no admin/product/cart/recipe/pantry/order features).

## Stack
- React + TypeScript
- Vite
- Tailwind CSS (v4 via `@tailwindcss/vite`)
- React Router
- Lucide React icons
- Supabase JS client (`@supabase/supabase-js`)

## Implemented
- **Phase 1:** Vite/TS/Tailwind/Router config, CookKart design tokens and global styles, responsive layout (header/nav/search UI/login-signup/admin placeholder, mobile nav, footer), homepage, route placeholders, external images with fallbacks.
- **Phase 2 (customer auth only):**
  - Reusable Supabase client (`src/services/supabaseClient.ts`) using env vars `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` (supports publishable or legacy anon keys)
  - Auth context/provider with session persistence, initial session check, and `onAuthStateChange` listener
  - Sign up (email/password, full name, confirm password, validation, loading/success/error states, full name stored in Supabase user metadata, email-confirmation handling)
  - Login (validation, auth error states, redirect to requested destination or My Kitchen)
  - Logout (Supabase sign-out, session cleared, redirect to homepage)
  - Protected route for `/my-kitchen` and guest-only routes for `/login` `/signup` (preserves requested destination)
  - Polished, accessible auth forms matching existing CookKart design; header updates for authenticated state
  - Clear configuration error UI when Supabase env vars are missing (no crash)

## Environment
Copy `frontend/.env.example` to `frontend/.env` and set:

```env
VITE_SUPABASE_URL=...
VITE_SUPABASE_ANON_KEY=...
```

Never commit `.env` or place service-role/DB credentials in frontend code.

## Phase 10 — Admin console

Protected `/admin` routes with a database-backed access check:

- `src/services/adminApi.ts` — authenticated admin API client (never sends a role).
- `src/features/admin/AdminAccessContext.tsx` — resolves access from `GET /api/admin/me`.
- `src/features/admin/AdminRoute.tsx` — redirects non-admins and unauthenticated users.
- `src/layouts/AdminLayout.tsx` and `src/pages/admin/*` — dashboard, orders, order detail and product availability screens with loading, error, empty and success states.

The Admin link is shown only after the backend confirms `profiles.is_admin`. Authorization always happens server-side; see the root `README.md` for the manual administrator configuration procedure.

## Out of scope
Supabase project setup verification beyond code-level handling, sales analytics, online payments/card processing, refunds, coupons, delivery tracking, and fake data. Cart, Cash on Delivery checkout, order history, pantry management, saved recipes, and recommendations are implemented; product and recipe catalogues are seeded in the database.

## Commands
Run from `frontend/`:

```bash
npm install
npm run dev
npm run build
npm run preview
```

