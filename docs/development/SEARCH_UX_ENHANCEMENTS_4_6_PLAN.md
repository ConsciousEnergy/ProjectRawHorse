# Search UX Enhancements (4–6) – Plan

## Scope

- **4. Search suggestions**: Autocomplete while typing in the global SearchBar.
- **5. Visual highlighting**: When opening a result from SearchBar, scroll to and flash/highlight the matching row in the Browse table.
- **6. Search history**: Show recently clicked search results (from the global SearchBar).

No edits to the backend or to any existing plan file. All work in the frontend.

---

## Current behavior

- **SearchBar** (`frontend/src/components/SearchBar.tsx`): Debounced (300ms) call to `searchGlobal(query)` when `query.length >= 2`. Dropdown shows full results only; no suggestions or history. On result click it navigates to `/browse?tab=...&search=...&highlight=${result.id}` and clears the input.
- **Browse** (`frontend/src/pages/Browse.tsx`): Reads URL params `tab`, `search`, `type`, `page` only; **does not read `highlight`**. Has `HighlightText` for in-cell search-term highlighting and `recentSearches` (localStorage key `recentSearches`) for **recent search terms** on the Browse page, not for “recently clicked results” from the global SearchBar. Table rows have no refs or data-row-id for scroll/highlight.

---

## 4. Search suggestions (autocomplete while typing)

**Goal:** As the user types, show helpful suggestions before or alongside API results (e.g. recent searches, or top results with a “suggestions” feel).

**Approach:**

- **Suggestions = recent search terms + recent clicked results**  
  When the dropdown is open and the user has typed at least 1 character (or 0), show a “Suggestions” block: “Recent searches” from a new localStorage key for global search terms (e.g. `searchBarRecentQueries`) and “Recent results” from enhancement 6. Tapping a suggestion either runs that query (recent term) or navigates again (recent result). No new API.
- Optionally use a slightly shorter debounce (e.g. 150ms) so the first batch of API results feels more like autocomplete.

**Implementation:**

1. **SearchBar state and storage**
   - Add `searchBarRecentQueries` in localStorage (e.g. last 10 strings). On each successful `searchGlobal` call with `query.length >= 2`, prepend `query`, de-dupe, slice to 10, save.
   - When dropdown opens and `query` is short (e.g. 0–1 chars), show “Recent searches” from `searchBarRecentQueries` (optionally filter by current `query`). Clicking one sets `query` to that term (triggers search) or runs search and shows results.
   - When dropdown opens with empty or short query, show “Recent results” from the clicked-results history (enhancement 6).

2. **UI**
   - In the dropdown: if `query.length < 2`, show only “Suggestions” (recent queries + recent clicked results). When `query.length >= 2`, show API results as today; optionally add a “Suggestions” section above them (e.g. matching recent queries).

No new API; reuses existing `searchGlobal`.

---

## 5. Visual highlighting (flash / highlight result row in Browse)

**Goal:** When the user lands on Browse from a SearchBar result click, the row that matches `highlight` should be brought into view and briefly highlighted (e.g. flash or background pulse).

**Implementation:**

1. **Read `highlight` in Browse**
   - In `frontend/src/pages/Browse.tsx`, read `highlightId = searchParams.get('highlight')` where `tab`, `search`, `type`, `page` are read. Ignore if empty.

2. **Row identity**
   - Give each table row a stable id matching what SearchBar sends:
     - Entities: `result.id` is `entity_id` → `id={\`row-entity-${entity.entity_id}\`}`.
     - Money flows: `result.id` is flow `id` → `id={\`row-flow-${flow.id}\`}`.
     - Awards: `result.id` is award `id` → `id={\`row-award-${award.id}\`}`.
     - FOIA: `result.id` is foia `id` → `id={\`row-foia-${foia.id}\`}`.

3. **Scroll into view**
   - After data is loaded and the table is rendered, if `highlightId` is set and the current tab’s data contains that id, get the row DOM node (e.g. `document.getElementById('row-entity-' + highlightId)`) and call `scrollIntoView({ behavior: 'smooth', block: 'nearest' })` once (e.g. in a `useEffect` that depends on `highlightId`, tab, and the loaded data).

4. **Flash / highlight style**
   - Add a CSS class (e.g. `.row-highlight-flash`) in `Browse.css` that applies a temporary background (e.g. `var(--color-primary)` at low opacity). Apply this class to the row that matches `highlightId` when it first mounts or when `highlightId` and data first align. Remove the class after 2–3 s or after a short CSS animation (e.g. `@keyframes flash` for a brief pulse).

5. **Cleanup**
   - After scrolling and starting the flash, optionally clear `highlight` from the URL so a refresh doesn’t re-trigger.

**Files:** `frontend/src/pages/Browse.tsx`, `frontend/src/pages/Browse.css`.

---

## 6. Search history (recently clicked results)

**Goal:** Persist the last N results that the user clicked in the global SearchBar and show them as “Recent results” so they can jump back quickly.

**Implementation:**

1. **Storage shape**
   - New localStorage key: `searchBarClickedResults`. Store a list of objects, e.g. `{ id, type, title }`. Cap at 5–8 items; prepend on each click, de-duplicate by `id` (and type), then slice.

2. **Write on click**
   - In SearchBar’s `handleResultClick`, before navigating: read current list from localStorage, prepend `{ id: result.id, type: result.type, title: result.title }`, de-dupe by id (and type), slice(0, 8), write back.

3. **Read and show in SearchBar**
   - When the dropdown is open and the query is short or empty, read `searchBarClickedResults` and render a “Recent results” section (e.g. above “Recent searches”). Each item is clickable and navigates to Browse with the same `tab`, `search`, `highlight` as a normal result click.

4. **Optional**
   - “Clear history” link in the dropdown footer that clears `searchBarClickedResults` and `searchBarRecentQueries`.

**Files:** `frontend/src/components/SearchBar.tsx`, `frontend/src/components/SearchBar.css` (if needed for “Recent results” styling).

---

## Order of work

1. **6. Search history** first: localStorage + `handleResultClick` update; then “Recent results” block in the dropdown.
2. **4. Search suggestions**: add `searchBarRecentQueries`, wire “Recent searches” and “Recent results” into the dropdown; optionally shorten debounce.
3. **5. Visual highlighting**: read `highlight` in Browse, row ids/refs, scrollIntoView, and flash CSS.

Suggested order: **6 → 4 → 5**.

---

## Files to touch (summary)

| File | Changes |
|------|--------|
| `frontend/src/components/SearchBar.tsx` | Recent queries + clicked-results storage; suggestions block (recent searches + recent results) in dropdown; optional shorter debounce. |
| `frontend/src/components/SearchBar.css` | Styles for “Suggestions” / “Recent results” / “Recent searches” if needed. |
| `frontend/src/pages/Browse.tsx` | Read `highlight`; add row `id` for entities, flows, awards, foia; scroll + flash logic; optional URL cleanup. |
| `frontend/src/pages/Browse.css` | `.row-highlight-flash` and optional `@keyframes` for pulse. |

No new API endpoints; no backend changes.
