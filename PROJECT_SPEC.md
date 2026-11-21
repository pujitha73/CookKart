# CookKart — Project Specification (Phase 0)

## 1. Purpose
CookKart is a full-stack grocery shopping and recipe discovery application. This document records the approved scope, exclusions, design direction, recipe catalogue requirements, and technology decisions established in Phase 0. It is the source of truth for future implementation phases.

## 2. Approved Functionality

### 2.1 Primary customer sections
1. **Shop**
   - Browse and purchase grocery and food products.
   - Product discovery, product details, and purchase flow are in scope for future phases (not implemented in Phase 0).

2. **Explore Recipes**
   - Browse recipes by cuisine, collection, and meal type.
   - Recipe discovery and detail experiences are in scope for future phases.

3. **My Kitchen**
   - Manage personal pantry information.
   - Manage saved recipes.

### 2.2 Additional customer features
4. **What Can I Cook Today?**
   - Recommend recipes using ingredients available in the user's kitchen.
   - Matching logic and UX to be implemented in later phases.

5. **Smart Recipe-to-Cart**
   - Identify missing recipe ingredients based on pantry/cart context.
   - Add corresponding grocery products to the shopping cart.

### 2.3 Other customer functionality
- Authentication (via Supabase Auth; no separate password system)
- Search
- Cart
- Wishlist
- Profile
- Order history

### 2.4 Admin access (limited)
- An admin access entry point may appear near customer login/signup.
- An **honest placeholder** is sufficient.
- **Out of scope:** admin dashboard, sales analytics, fabricated administrative data, or any admin management functionality beyond a placeholder entry point.

## 3. Excluded Functionality
- Building homepage or shopping/recipe UI in Phase 0
- Implementing authentication screens or flows in Phase 0
- Building product or recipe interfaces in Phase 0
- Generating fake customer data, fake orders, or sales records
- Generating recipe or product seed data in Phase 0
- Creating database migrations or production tables before configuration
- Implementing future phases beyond architecture/scaffolding/documentation
- Introducing additional major features without approval
- Downloading/storing image or video media files locally
- Inventing or generating unverified external media URLs

## 4. Design Direction (for Phase 1+)

### 4.1 Visual palette (approved)
- Deep forest green
- Dark green
- Warm cream
- Lime green accents
- Muted sage green

### 4.2 Brand and UI characteristics
- Premium modern food and grocery brand feel
- Editorial typography
- High-quality food photography
- Spacious layouts
- Beautiful product and recipe cards
- Rounded corners
- Subtle animations and transitions
- Responsive layouts for desktop, tablet, and mobile
- Login/signup area may feature a distinctive branded visual

> Note: No actual visual pages are created in Phase 0; these requirements guide future UI implementation.

## 5. Recipe Catalogue Requirements (Planned Data)

### 5.1 Collections and counts
Plan for **25 unique recipes** across **5 collections**:
- South Indian: 5
- North Indian: 5
- Chinese: 5
- Italian: 5
- Quick Meals: 5

**Quick Meals** is a convenience-based collection, not a cuisine.

### 5.2 Meal-type distribution per collection
Each collection must eventually contain:
- 2 breakfast/tiffin recipes
- 2 lunch/dinner recipes
- 1 snack recipe

Meal-type filters must work across all collections **without duplicating recipe records**.

### 5.3 Recipe fields (required support)
Every recipe must support:
- Name and description
- Cuisine/collection
- Meal type
- Preparation and cooking time
- Difficulty
- Serving size
- Image reference
- Ingredients and quantities
- Cooking instructions
- YouTube video ID or validated video URL

### 5.4 Ingredient and product scale (planned)
- Approximately **60–70 unique ingredients**
- Approximately **50–60 grocery products**

> No recipe or product seed data is generated in Phase 0.

## 6. Technology Decisions (Approved)

### 6.1 Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- React Router

### 6.2 Backend
- Python **3.12.7** (backend development version)
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### 6.3 Database and authentication
- Supabase PostgreSQL
- Supabase Auth (identity and authentication)
- No separate password system

### 6.4 Development tooling
- Git
- Python virtual environment
- npm
- Environment variables

### 6.5 Constraints
- Do not introduce unnecessary frameworks or dependencies
- Keep UI components, business logic, API routes, and database access separate
- Preserve existing files and working code (inspect before changes)

## 7. Media Architecture Requirements (Planned)
- Use external optimized image URLs (no local media storage)
- Responsive image delivery
- Appropriate loading priorities
- Lazy loading for below-the-fold images
- Loading placeholders and fallback images
- YouTube privacy-enhanced embedded players
- Load recipe video player when the recipe detail page opens
- Avoid unnecessary video loading for unopened recipes
- Store media references in PostgreSQL
- Do not invent or generate unverified external URLs

## 8. Environment and Security Requirements
- Use Python 3.12.7 and plan a Python virtual environment
- Keep frontend and backend environment variables separate where appropriate
- Never commit `.env` files
- Never place Supabase service-role keys or database credentials in frontend code
- Plan secure authentication and user data isolation (RLS)
- Do not expose secrets in logs or documentation

## 9. Phase 0 Deliverables
- Inspected project and environment
- Initial frontend/backend/docs folder structure
- Documentation: `README.md`, `PROJECT_SPEC.md`, `ARCHITECTURE.md`, `AGENTS.md`
- `.gitignore` and `.env.example` with placeholders only
- No migrations, no seed data, no customer-facing implementation
