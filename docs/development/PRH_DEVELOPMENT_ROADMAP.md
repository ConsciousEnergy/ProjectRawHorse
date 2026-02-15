# Project RawHorse - Development Roadmap

**Purpose:** Persistent, actionable development guide based on codebase audit (PRH v0.4.1Beta).  
**Last Updated:** February 2026  
**Status:** Living document — update as items are completed or priorities change.

---

## P0 — Immediate Fixes (Do Now)

### 1. Analysis Overview Card Icon Gradients
**Status:** Done (v0.4.1Beta).  
**Detail:** Entity Network Graph and Sankey Flow Diagram now have distinct gradients:
- Entity Network Graph: `linear-gradient(135deg, #5B4FFF, #7c6fff)` (purple)
- Sankey Flow Diagram: `linear-gradient(135deg, #D4A218, #FFD700)` (gold)
- Intelligence Stack Pyramid: red-orange (unchanged)
- FOIA Targets: green-teal (unchanged)

**File:** `frontend/src/pages/AnalysisOverview.tsx`

### 2. ESLint Configuration
**Status:** TODO.  
**Issue:** Frontend has no `.eslintrc` (or equivalent); `npm run lint` fails with "ESLint couldn't find a configuration file."  
**Action:** Add ESLint config (e.g. `frontend/.eslintrc.cjs` or `eslint.config.js`) so `npm run lint` runs successfully. Consider aligning with existing `package.json` script: `eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0`.

---

## P1 — Code Quality & Refactoring (Next Sprint)

### 3. Refactor Browse.tsx (965 lines)
**File:** `frontend/src/pages/Browse.tsx`  
**Goal:** Split into smaller, testable units.

| Extract | Description |
|--------|-------------|
| `BrowseFilters.tsx` | Filter panel: entity type, amount range, date, agency, quick filters |
| `BrowseTable.tsx` | Table rendering per tab (entities, money flows, awards, FOIA) |
| `useBrowseData.ts` | Custom hook: data fetching, pagination, sorting logic |
| `useBrowseFilters.ts` | Custom hook: filter state and URL sync |
| Optional | `useReducer` to replace 15+ `useState` calls |

**Additional:** Extract `SortableHeader` and `HighlightText` from inline definitions into shared components.

### 4. Other Large Files
- **Contribute.tsx** (508 lines): Split form sections into sub-components (e.g. EntityForm, MoneyFlowForm, AwardForm, FOIAForm).
- **SearchBar.tsx** (420 lines): Extract search result list and result item into separate components.

### 5. Move Inline CSS from AnalysisOverview.tsx
**File:** `frontend/src/pages/AnalysisOverview.tsx`  
**Issue:** 150+ lines of CSS in a `<style>` tag inside JSX.  
**Action:** Move to `frontend/src/pages/AnalysisOverview.css` and import. Keeps JSX focused and allows reuse/tooling.

---

## P1 — TypeScript Type Safety

### 6. API Layer Types (`frontend/src/services/api.ts`)
**Issue:** 20+ `any` types in params and contribution payloads.

**Actions:**
- Define `EntityParams`, `MoneyFlowParams`, `AwardParams`, `FOIAParams` (and any other query shapes) in `frontend/src/types/` or in `api.ts`.
- Type contribution functions: replace `entity: any`, `moneyFlow: any`, etc. with proper interfaces (e.g. `EntityInput`, `MoneyFlowInput`).
- Add a custom `ApiError` class and use it in error handling so callers can distinguish API failures.

### 7. Browse.tsx Types
- Line ~204: `params: any` — type as a union or discriminated type based on `activeTab` (entities | money-flows | awards | foia).
- Line ~290: `sortFn(a: any, b: any)` — use generics or concrete row types (e.g. `Entity | MoneyFlow | Award | FOIATarget`).

### 8. Other Files
- **Analysis.tsx:** Replace `financialData: any`, `timelineData: any` with defined interfaces.
- **types/index.ts:** Replace `metadata: any` with `Record<string, unknown>` or a concrete type.

---

## P1 — React Best Practices

### 9. useEffect Dependencies
- **Browse.tsx** (line ~201): `loadData` used in `useEffect` but not in dependency array — wrap `loadData` in `useCallback` (with correct deps) or define it inside the effect.
- **NetworkGraph.tsx** (line ~112): `loadGraphData` in `useEffect` — wrap in `useCallback` or define inside effect.
- **SankeyDiagram.tsx** (line ~98): `renderSankey` in `useEffect` deps — wrap in `useCallback`.

### 10. API Error Handling
- **Current:** `api.ts` functions have no try/catch; errors propagate to callers.
- **Actions:** Add Axios response/error interceptor for centralized handling; optional retry for transient failures; map to user-friendly messages or `ApiError`.

---

## P2 — Security Hardening (Before Production)

### HIGH priority
1. **Remove hardcoded demo credentials** — `backend` auth (e.g. `auth.py` ~302–307): remove or gate demo user (e.g. password "admin") so it never loads in production.
2. **Require bcrypt** — Fail securely if bcrypt unavailable; do not fall back to plaintext password comparison.
3. **AUTH_ENABLED for production** — Ensure production config sets `AUTH_ENABLED=true` (default is currently `False`).
4. **SECRET_KEY** — Do not use default "dev-secret-key-change-in-production" in production; use a strong, secret value (e.g. from env).
5. **Content-Security-Policy** — Add CSP header in backend middleware to reduce XSS risk.

### MEDIUM priority
6. **Export endpoints** — Add authentication (or at least rate limiting) to export routes (`export_router.py`).
7. **Rate limiting** — Apply rate limits to analysis (and other expensive) endpoints.
8. **CORS** — Make allowed origins configurable via environment variable instead of hardcoding (e.g. localhost:3000).
9. **HTTPS** — Enforce HTTPS in production (redirect or middleware).
10. **User store** — Replace in-memory user store with a database-backed store for production.

### LOW priority
11. Global exception handler in FastAPI for consistent error responses.  
12. Request ID tracking for debugging and logs.  
13. Security/audit logging for sensitive actions.  
14. Validate GitHub token format in contribute router before use.  
15. API versioning (e.g. `/api/v1/...`).

---

## P2 — Testing

### 16. Backend
- Add pytest tests for core routes: data (entities, flows, awards, FOIA), search, export, analysis.
- Use TestClient from FastAPI; mock or use test DB where appropriate.

### 17. Frontend
- Add React Testing Library tests for critical flows: e.g. Dashboard, Browse (filters/tabs), Analysis overview, FOIA table.
- Test key components: SearchBar, ScoreBadge, ErrorBoundary, EmptyState.

### 18. Integration
- Add integration tests for API workflows (e.g. search → entity detail, export CSV).

---

## P3 — Performance (Future)

### 19. Frontend bundle
- Address Vite warning: single large JS chunk (~540KB). Use code-splitting (e.g. `React.lazy` + `Suspense`) for Analysis sub-pages (Network Graph, Sankey, Pyramid, FOIA).
- Lazy-load heavy visualizations to improve initial load.

### 20. Backend
- Consider Redis (or similar) caching for expensive analysis/search queries.
- Review N+1 queries and add eager loading where needed.

### 21. Browse tables
- For large result sets, consider virtual scrolling (e.g. react-window) to keep DOM small.

---

## P3 — Infrastructure (Future)

### 22. Code style and hooks
- Add Prettier and align with ESLint (e.g. `eslint-config-prettier`).
- Add pre-commit hooks (e.g. husky + lint-staged) to run lint and format.

### 23. CI/CD
- GitHub Actions (or equivalent): on PR run frontend build, lint, and (when available) tests; backend tests.
- Environment-specific configs (dev/staging/prod) for API URL, feature flags, auth.

### 24. Documentation
- Keep this roadmap updated as P0–P2 items are completed.
- Update ARCHITECTURE.md and API docs when adding versioning or new security middleware.

---

## Reference: Audit Summary

- **Security:** ORM in use (SQL injection mitigated); validation and sanitization present; security headers and rate limiting exist. Weak spots: auth defaults, demo credentials, plaintext password fallback, missing CSP, unauthenticated exports.
- **Code quality:** TypeScript used but `any` is common in API and some pages; several files exceed 200–300 lines; a few `useEffect` dependency issues. Strengths: clear structure, accessibility, and use of hooks.
- **Testing:** No automated tests yet; adding tests is P2.

Use this document to pick the next task by priority (P0 → P1 → P2 → P3) and update the status as work is completed.
