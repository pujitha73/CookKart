# CookKart — Architecture (Phase 0)

## 1. Overview
CookKart is planned as a full-stack application with a clear separation between a React/TypeScript frontend and a FastAPI/Python backend, using Supabase (PostgreSQL + Auth) for data persistence and identity. Phase 0 establishes structure, conventions, and design decisions only; no customer-facing features, migrations, or production integrations are implemented.

## 2. Frontend/Backend Architecture

### 2.1 Repository layout (approved baseline)
```text
CookKart/
  frontend/
    src/
      assets/        # Static UI assets (non-user media; no downloaded product/recipe media)
      components/    # Reusable presentational/UI components
      layouts/       # App/page layout shells
      pages/         # Route-level page containers
      features/      # Feature modules (shop, recipes, kitchen, auth, cart, etc.)
      hooks/         # Reusable React hooks
      services/      # API client/service wrappers
      types/         # Shared TypeScript types/interfaces
      utils/         # Pure utility helpers
    public/
  backend/
    app/
      api/           # FastAPI routers/endpoints
      core/          # Settings, security, dependencies, config
      models/        # SQLAlchemy ORM models
      schemas/       # Pydantic request/response schemas
      services/      # Business logic/use-case orchestration
      repositories/  # Data access layer (DB queries)
      database/      # DB session/engine/base, Supabase/Postgres integration helpers
      utils/         # Backend utilities
    migrations/      # Alembic migrations (planned; not run in Phase 0)
    tests/           # Backend tests
  docs/              # Additional documentation (optional expansion)
```

### 2.2 Separation of concerns
- **UI components (`frontend/src/components`, `layouts`, `pages`)**: rendering and interaction composition only.
- **Frontend feature/business logic (`features`, `hooks`)**: state orchestration and feature workflows; avoid embedding raw data-access details in UI.
- **Frontend API layer (`services`)**: HTTP calls, request/response mapping, and error normalization.
- **Backend API routes (`backend/app/api`)**: HTTP contract, validation wiring, auth dependencies; no direct complex business rules.
- **Backend services (`backend/app/services`)**: business logic (e.g., recipe recommendations, missing-ingredient/cart matching rules).
- **Backend repositories (`backend/app/repositories`)**: database access and query composition.
- **Models/schemas**: ORM persistence models and API/data validation schemas kept distinct.

### 2.3 Technology choices
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, React Router
- **Backend:** Python 3.12.7, FastAPI, Pydantic, SQLAlchemy, Alembic
- **Database/Auth:** Supabase PostgreSQL, Supabase Auth
- **Dev:** Git, Python virtual environment, npm, environment variables

## 3. Database Architecture Planning (Supabase PostgreSQL)

> Schema below is a Phase 0 design plan. No migrations or production tables are created in Phase 0.

### 3.1 Core entities and relationships

#### Identity/profile
- **`auth.users` (Supabase-managed)**: source of truth for authentication identity.
- **`profiles`**: application profile data linked 1:1 to `auth.users`.
  - `id` (PK, UUID, FK -> `auth.users.id`)
  - display name, avatar URL (optional external), preferences/metadata (as needed)
  - timestamps

#### Catalog: products and categories
- **`product_categories`**
  - `id` (PK), `name` (unique), `slug` (unique), description, timestamps
- **`products`**
  - `id` (PK), `category_id` (FK -> `product_categories.id`)
  - name, slug (unique), description, price, unit/size, image_url (external), availability flags, timestamps
  - indexes: `category_id`, searchable name/slug fields as appropriate

#### Recipes, collections, ingredients
- **`recipe_collections`** (e.g., South Indian, North Indian, Chinese, Italian, Quick Meals)
  - `id` (PK), `name` (unique), `slug` (unique), type/cuisine label, timestamps
- **`recipes`**
  - `id` (PK), `collection_id` (FK -> `recipe_collections.id`)
  - name, slug (unique), description
  - `meal_type` (breakfast/tiffin, lunch/dinner, snack) to support cross-collection filtering without duplicating records
  - prep_time_minutes, cook_time_minutes, difficulty, serving_size
  - image_url (external), youtube_video_id or validated youtube_url/reference, timestamps
  - indexes: `collection_id`, `meal_type`
- **`ingredients`** (canonical ingredient master, ~60–70 planned)
  - `id` (PK), `name` (unique normalized name), optional aliases/metadata, timestamps
- **`recipe_ingredients`** (junction with quantities)
  - `id` (PK) or composite PK (`recipe_id`, `ingredient_id`, line/order as needed)
  - `recipe_id` (FK -> `recipes.id`), `ingredient_id` (FK -> `ingredients.id`)
  - quantity, unit, preparation note, display order
  - unique constraint to prevent unintended duplicate ingredient rows per recipe position

#### Product-to-ingredient mapping (Smart Recipe-to-Cart)
- **`product_ingredient_mappings`**
  - `id` (PK) or composite PK (`product_id`, `ingredient_id`)
  - `product_id` (FK -> `products.id`), `ingredient_id` (FK -> `ingredients.id`)
  - match strength/priority or substitution notes (optional) to select best grocery product
  - unique constraint on (`product_id`, `ingredient_id`)
  - indexes on both FKs for lookup in both directions

#### User kitchen and saved content
- **`user_pantry`** (user-specific)
  - `id` (PK), `user_id` (FK -> `auth.users.id`/`profiles.id`), `ingredient_id` (FK -> `ingredients.id`)
  - quantity/unit/availability state, timestamps
  - unique constraint on (`user_id`, `ingredient_id`) where appropriate
- **`saved_recipes`** (user-specific)
  - `id` (PK) or composite PK (`user_id`, `recipe_id`)
  - `user_id` (FK), `recipe_id` (FK -> `recipes.id`), timestamps
  - unique constraint on (`user_id`, `recipe_id`)

#### Shopping and orders
- **`shopping_carts`** (user-specific, typically one active cart per user)
  - `id` (PK), `user_id` (FK), status/metadata, timestamps
  - unique/partial uniqueness strategy for active cart per user (planned)
- **`cart_items`**
  - `id` (PK), `cart_id` (FK -> `shopping_carts.id`), `product_id` (FK -> `products.id`)
  - quantity, unit price snapshot reference strategy (planned), timestamps
  - unique constraint on (`cart_id`, `product_id`) for quantity aggregation (if chosen)
- **`orders`** (user-specific)
  - `id` (PK), `user_id` (FK), order status, totals, placed_at, timestamps
- **`order_items`**
  - `id` (PK), `order_id` (FK -> `orders.id`), `product_id` (FK -> `products.id`, nullable/set-null policy to be defined)
  - quantity, purchased price snapshot, line total snapshot, timestamps

#### Wishlist
- **`wishlist`** (user-specific)
  - `id` (PK) or composite PK (`user_id`, `product_id`)
  - `user_id` (FK), `product_id` (FK -> `products.id`), timestamps
  - unique constraint on (`user_id`, `product_id`)

### 3.2 Keys, constraints, and indexes (design principles)
- **Primary keys:** UUIDs or database-generated identifiers consistently applied (final choice documented during implementation).
- **Foreign keys:** enforce referential integrity across all relationships; define `ON DELETE`/`ON UPDATE` behaviors explicitly during migration design.
- **Unique constraints:** slugs/natural identifiers where applicable; user-item junction uniqueness to prevent duplicates.
- **Indexes:** FKs and common filter/sort fields (`collection_id`, `meal_type`, `category_id`, user-owned record lookups).
- **Normalization:** avoid redundant storage; store snapshots only where historically necessary (e.g., order item price/line totals).

### 3.3 Row Level Security (RLS) planning
- Enable RLS on all user-owned tables (`profiles`, `user_pantry`, `saved_recipes`, `shopping_carts`, `cart_items`, `orders`, `order_items`, `wishlist`).
- Policies must ensure users can only read/write their own records, linked to authenticated Supabase user identity (`auth.uid()`).
- Public/catalog tables (`products`, `product_categories`, `recipes`, `recipe_collections`, `ingredients`, `recipe_ingredients`, `product_ingredient_mappings`) should use read policies appropriate for customer browsing; write access restricted to privileged/admin contexts (future scope) and never via frontend secrets.
- Backend service-role access (if ever used) must remain server-side only and tightly scoped.

## 4. Authentication Design
- **Provider:** Supabase Auth is the sole identity/authentication system.
- **No separate password system:** application must not implement custom credential storage or password hashing.
- **Identity linkage:** user-specific records reference the Supabase-authenticated user (`auth.users.id` / profile linkage).
- **Frontend:** uses public Supabase anon configuration only for client auth/session flows; never embeds service-role or DB credentials.
- **Backend:** validates Supabase JWTs/tokens for protected API operations (implementation detail in later phases) and enforces authorization in combination with RLS-aware data access patterns.
- **Admin placeholder:** UI entry point only; no admin privileges, analytics, or fabricated data.

## 5. API Design Conventions (Planned)

### 5.1 General
- Base style: RESTful JSON APIs via FastAPI.
- Versioning strategy reserved (e.g., `/api/v1`) to be finalized at implementation; keep routes organized by domain (`shop`, `recipes`, `kitchen`, `cart`, etc.).
- Use Pydantic schemas for request/response validation and serialization.
- Keep route handlers thin; delegate business logic to services and data access to repositories.

### 5.2 Auth and authorization
- Protected endpoints require authenticated Supabase user context.
- Enforce ownership checks for user-specific resources; never trust client-supplied user IDs for authorization decisions.

### 5.3 Errors and responses
- Consistent error envelope and HTTP status usage (validation errors, auth errors, not found, conflicts).
- No secrets or sensitive internals in error messages/logs.

### 5.4 Performance and UX support
- Pagination/filter/sort conventions for product and recipe listings.
- Endpoints shaped to support responsive UI needs (cards, detail views, recommendations) without over-fetching.

## 6. Media Handling (Planned)
- **No local media storage/downloads** for images or videos.
- Store **external optimized image URLs** and **YouTube video IDs/validated URLs** in PostgreSQL.
- Frontend responsibilities (future): responsive image delivery (`srcset`/sizes as applicable), appropriate loading priorities, lazy loading below-the-fold images, loading placeholders and fallback images.
- Recipe detail video: load YouTube **privacy-enhanced** embedded player when the recipe detail page opens; avoid unnecessary video loading for unopened recipes.
- **Do not invent or generate unverified external URLs.**

## 7. Security Considerations
- **Secrets management:** never commit `.env` files; `.env.example` contains placeholders only.
- **Credential boundaries:** Supabase service-role keys and database credentials must never appear in frontend code, logs, or docs.
- **Environment separation:** keep frontend and backend environment variables separate where appropriate (`VITE_*` for public frontend config; server-only secrets in backend env).
- **Auth/data isolation:** Supabase Auth for identity, RLS for user-owned data, backend authorization checks for protected operations.
- **Least privilege:** prefer anon/authenticated client access patterns; restrict privileged operations to secure server contexts.
- **Input validation:** Pydantic schemas and backend validation for all incoming data.
- **Dependency discipline:** introduce only approved/necessary frameworks and packages.

## 8. Phase 0 Boundaries
- Architecture, scaffolding, and documentation only.
- No homepage/shopping/recipe/auth UI implementation.
- No fake data, no seed generation, no migrations run, and no database credentials configured in the application. Manual Supabase configuration remains a later step.