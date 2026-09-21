# Leagle Intelligence Repository Audit

This report outlines the structural, UI/UX, and architectural findings in the Leagle-Assistance repository. It serves as a prioritized action plan to align the codebase with established conventions, security best practices, and performance standards.

## Phase 1: Repository Orientation
- **Frontend**: Next.js 16 (App Router), React 19, Tailwind CSS v4, shadcn, Clerk (auth), Zustand, and React Query. Note that despite TS config (`tsconfig.json`), many files use `.jsx` extensions.
- **Backend**: FastAPI, SQLAlchemy (asyncpg), Alembic for migrations, Qdrant Client for vector search, LangChain.
- **Documentation**: `ARCHITECTURE_GUIDE.md` specifies an architecture where a message queue (Celery/Redis) handles extraction and embedding asynchronously, but current implementations often execute these synchronously within the request lifecycle.
- **Quality Assurance**: Minimal test configuration observed. Missing global error boundary patterns in the frontend.

---

## Phase 4: Prioritized Findings

### 1. Critical

**Security: Missing Authentication on Sensitive API Routes**
- **File**: `backend/main.py` (Lines 92-98), `backend/routers/regulations.py`
- **What**: The main FastAPI router includes `/api/regulations`, `/api/impact`, and other sensitive routes without requiring authentication or injecting a `Depends(get_current_user)` check.
- **Why it matters**: Any unauthenticated user can invoke ingestion, trigger full system syncs, or read proprietary impact analyses, leading to potential data manipulation and denial of service.
- **Suggested fix**: Apply global authentication dependencies to these routers or protect specific endpoints using Clerk/JWT verification.

### 2. High Impact

**Performance: Synchronous Background Work in Request Lifecycle**
- **File**: `backend/routers/regulations.py` (Lines 62, 84)
- **What**: `await run_impact_analysis(db, regulation)` is called directly inside the `POST /ingest` and `/upload-pdf` endpoint handlers.
- **Why it matters**: Document ingestion and impact analysis are heavy LLM and vector tasks. Doing them synchronously blocks the HTTP response, leading to timeouts and a degraded user experience. This also violates the planned Phase 2 architecture in `ARCHITECTURE_GUIDE.md`.
- **Suggested fix**: Dispatch these heavy tasks to a background worker (e.g., Celery) or use FastAPI's `BackgroundTasks`.

**Performance: Sequential-When-Parallel-Possible (Independent DB Queries)**
- **File**: `backend/routers/impact.py` (Lines 19, 24)
- **What**: `reg_result` and `pol_result` are fetched sequentially: `await db.execute(...)` for regulation, then `await db.execute(...)` for policy. 
- **Why it matters**: These two database reads do not depend on each other. Waiting for them sequentially increases latency unnecessarily. 
- **Suggested fix**: Use `await asyncio.gather(db.execute(req_query), db.execute(pol_query))` to fetch both concurrently.

**Performance: Sequential Sync Loop**
- **File**: `backend/services/sync_manager.py` (Lines 59-61)
- **What**: The `sync_all_jurisdictions` function iterates over `JURISDICTION_REGISTRY` and `await`s each sync function sequentially. (Note: The code claims this is to "avoid overwhelming the database", but it could be optimized).
- **Why it matters**: Running 17 jurisdiction syncs sequentially makes the global sync extremely slow.
- **Suggested fix**: Use `asyncio.gather` with a bounded semaphore to parallelize syncs (e.g., 3 at a time) to balance speed and resource constraints.

**Performance: Unbounded Database Queries & Missing Pagination**
- **File**: `backend/routers/regulations.py` (Line 98)
- **What**: The list endpoint returns `.limit(500)` without offering `skip` or `offset` query parameters.
- **Why it matters**: As the regulation database grows, clients cannot paginate beyond the first 500 records, and fetching 500 records by default inflates response payload sizes.
- **Suggested fix**: Introduce standard `skip: int = 0` and `limit: int = 100` query parameters.

### 3. Medium

**Performance: Unoptimized Images in Next.js**
- **File**: `frontend/src/app/page.jsx` (Line 162), `frontend/src/app/components/Dashboard.jsx` (Line 68)
- **What**: The application uses raw HTML `<img>` tags for images (e.g., `<img src="/logo.png" />`).
- **Why it matters**: Raw `img` tags bypass Next.js's built-in image optimization (WebP conversion, lazy loading, proper sizing), degrading page load performance and Core Web Vitals.
- **Suggested fix**: Replace raw `<img>` tags with Next.js `next/image` (`<Image src="..." />`).

**Consistency: Ad-hoc Button Styling vs. Design System**
- **File**: `frontend/src/app/page.jsx` (Line 96, 108, 133)
- **What**: UI elements like the "Initialize Pulse" button are constructed with raw Tailwind classes (`<button className="w-full py-4 bg-white/5 border border-white/10 text-white text-[9px] font-black uppercase tracking-widest...">`).
- **Why it matters**: This leads to code duplication, makes global design changes difficult, and ignores the installed `shadcn` component library.
- **Suggested fix**: Extract these styles into a reusable `shadcn` UI `Button` variant (e.g., `variant="premium"`).

**Error Handling / UX: Swallowed API Errors on Dashboard**
- **File**: `frontend/src/app/components/Dashboard.jsx` (Lines 36-39)
- **What**: If the `getRegulations` or `getAlerts` promises fail, the error is caught, logged to the console, and `loading` is set to false. The dashboard proceeds to render `0` for all stats.
- **Why it matters**: Users will see a blank or zeroed-out dashboard without knowing there is a backend connectivity issue, causing confusion.
- **Suggested fix**: Store the error in state and display an inline error message or fallback UI to the user.

**Accessibility: Non-Semantic Layouts & Form Elements**
- **File**: `frontend/src/app/page.jsx` (Lines 28-46)
- **What**: Multiple interactive layout groups use `<div>` instead of semantic HTML (e.g., `<nav>`, `<main>`), and the "Initialize Scanning" element is wrapped inappropriately with nested interactive elements.
- **Why it matters**: Screen readers rely on semantic boundaries to navigate pages. Non-semantic layouts make the site difficult or impossible for visually impaired users to use.
- **Suggested fix**: Use semantic HTML5 elements (`<section>`, `<article>`, `<nav>`) and ensure all interactive elements have proper `aria-labels` and keyboard focus states.

### 4. Low / Nice-to-have

**Code Organization: Inline Component Definitions**
- **File**: `frontend/src/app/page.jsx` (Lines 180-193)
- **What**: The `CapabilityCard` component is defined at the bottom of `page.jsx` instead of in its own file.
- **Why it matters**: Makes the main page file longer than necessary and prevents reusing `CapabilityCard` elsewhere.
- **Suggested fix**: Move `CapabilityCard` into `frontend/src/app/components/CapabilityCard.jsx`.

**Accessibility / Polish: Poor Alt Text**
- **File**: `frontend/src/app/components/Dashboard.jsx` (Line 68)
- **What**: The image tag uses `alt="L"`.
- **Why it matters**: This does not convey meaning to screen readers or when the image fails to load.
- **Suggested fix**: Update alt text to a descriptive value like `alt="Leagle Logo"`.

**Consistency: Incomplete TypeScript Adoption**
- **File**: `frontend/src/app/page.jsx`, `frontend/src/app/components/Dashboard.jsx`
- **What**: Core files use `.jsx` extensions despite a `.tsx` / TypeScript setup (`tsconfig.json`) existing in the repo.
- **Why it matters**: You lose the benefits of prop type-checking, autocompletion, and safer refactoring that TypeScript provides.
- **Suggested fix**: Rename `.jsx` files to `.tsx` and explicitly type component props and state.
