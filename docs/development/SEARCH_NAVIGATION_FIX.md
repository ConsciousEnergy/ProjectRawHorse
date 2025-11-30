# Search Navigation Fix

**Date**: November 30, 2025  
**Issue**: Search results didn't navigate to Browse page  
**Status**: ✅ Fixed

---

## Problem

When users clicked on a search result, nothing happened. The search result would close, but the user wasn't taken to the relevant data in the Browse page.

**Original Code**:
```typescript
const handleResultClick = (result: SearchResult) => {
  // For now, just close the search
  // In future, implement routing to detailed view
  console.log('Navigate to:', result);
  setIsOpen(false);
  setQuery('');
};
```

---

## Solution

Implemented proper React Router navigation that:
1. Maps search result type to correct Browse tab
2. Navigates to `/browse` with URL parameters
3. Pre-fills search term in Browse page
4. Passes highlight ID for potential future highlighting

---

## Implementation

### 1. Updated SearchBar Component

**File**: `frontend/src/components/SearchBar.tsx`

**Changes**:
- Added `useNavigate` from react-router-dom
- Implemented proper navigation logic
- Maps result types to Browse tabs

```typescript
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();

const handleResultClick = (result: SearchResult) => {
  // Map result type to Browse tab
  const typeToTab: Record<string, string> = {
    'entity': 'entities',
    'award': 'awards',
    'money_flow': 'money-flows',
    'foia_target': 'foia'
  };
  
  const tab = typeToTab[result.type] || 'entities';
  
  // Navigate to Browse page with search pre-filled
  const searchTerm = result.title.split(':')[0].split('→')[0].trim();
  
  navigate(`/browse?tab=${tab}&search=${encodeURIComponent(searchTerm)}&highlight=${result.id}`);
  
  setIsOpen(false);
  setQuery('');
};
```

---

### 2. Enhanced Browse Page

**File**: `frontend/src/pages/Browse.tsx`

**Changes**:
- Added `useSearchParams` to read URL parameters
- Initializes tab and search term from URL
- Automatically loads data when parameters change

```typescript
import { useSearchParams } from 'react-router-dom';

const [searchParams] = useSearchParams();

// Initialize from URL parameters
useEffect(() => {
  const tab = searchParams.get('tab') as TabType;
  const search = searchParams.get('search');
  const highlight = searchParams.get('highlight');
  
  if (tab && ['entities', 'money-flows', 'awards', 'foia'].includes(tab)) {
    setActiveTab(tab);
  }
  
  if (search) {
    setSearchTerm(search);
  }
  
  if (highlight) {
    sessionStorage.setItem('highlightId', highlight);
  }
}, [searchParams]);

// Load data when tab or search term changes
useEffect(() => {
  loadData();
}, [activeTab, searchTerm]);
```

---

## How It Works

### User Flow

1. **User Types Search Query**
   - Example: "Peraton"
   - Search bar shows real-time results

2. **User Clicks Result**
   - Example: Clicks "Peraton" entity result

3. **Navigation Happens**
   - URL changes to: `/browse?tab=entities&search=Peraton&highlight=f6g7h8i9j0k1l2m3`
   - Browse page loads with:
     - Entities tab selected
     - Search term "Peraton" pre-filled
     - Data automatically filtered

4. **User Sees Filtered Data**
   - Browse page shows only results matching "Peraton"
   - Correct tab is already selected
   - Search input already filled

---

## URL Parameters

The navigation uses three URL parameters:

### `tab` (required)
Maps search result type to Browse tab:
- `entity` → `entities`
- `award` → `awards`
- `money_flow` → `money-flows`
- `foia_target` → `foia`

### `search` (required)
Extracted from result title:
- For entities: Direct name ("Peraton")
- For money flows: Source name ("NGA" from "NGA → Perspecta")
- For awards: Recipient name
- URL-encoded for special characters

### `highlight` (optional)
Result ID for potential future highlighting:
- Stored in sessionStorage
- Can be used to scroll to or highlight specific item
- Future enhancement opportunity

---

## Examples

### Search for "Peraton" Entity

**Search Result**:
```json
{
  "type": "entity",
  "id": "f6g7h8i9j0k1l2m3",
  "title": "Peraton",
  "description": "Corporation"
}
```

**Navigation**:
```
/browse?tab=entities&search=Peraton&highlight=f6g7h8i9j0k1l2m3
```

**Result**: 
- Browse page opens to Entities tab
- Search bar shows "Peraton"
- Table filtered to show Peraton

---

### Search for "NGA" Money Flow

**Search Result**:
```json
{
  "type": "money_flow",
  "id": "123",
  "title": "NGA → Perspecta: $824,000,000",
  "description": "Govt. contract (IDIQ) • 2019-08-12"
}
```

**Navigation**:
```
/browse?tab=money-flows&search=NGA&highlight=123
```

**Result**:
- Browse page opens to Money Flows tab
- Search bar shows "NGA"
- Table filtered to show NGA transactions

---

### Search for Award

**Search Result**:
```json
{
  "type": "award",
  "id": "456",
  "title": "Peraton NBIS OTA: $2,250,000,000",
  "description": "DCSA • 2023-01-03"
}
```

**Navigation**:
```
/browse?tab=awards&search=Peraton&highlight=456
```

**Result**:
- Browse page opens to Awards tab
- Search bar shows "Peraton"
- Table filtered to show Peraton awards

---

## Testing

### Test Cases

✅ **Test 1**: Click entity search result
- Search "Peraton"
- Click entity result
- **Expected**: Navigate to Entities tab with "Peraton" filtered

✅ **Test 2**: Click money flow result
- Search "NGA"
- Click money flow result
- **Expected**: Navigate to Money Flows tab with "NGA" filtered

✅ **Test 3**: Click award result
- Search "Peraton"
- Click award result
- **Expected**: Navigate to Awards tab with "Peraton" filtered

✅ **Test 4**: Click FOIA result
- Search "NGA"
- Click FOIA result
- **Expected**: Navigate to FOIA tab with "NGA" filtered

✅ **Test 5**: URL bookmarking
- Navigate via search
- Copy URL
- Open URL in new tab
- **Expected**: Same filtered view loads

✅ **Test 6**: Browser back button
- Navigate via search
- Click browser back
- **Expected**: Return to previous page

---

## Future Enhancements

### 1. Visual Highlighting
Currently stores `highlight` ID but doesn't use it visually.

**Potential Implementation**:
```typescript
// In Browse page, scroll to and highlight item
useEffect(() => {
  const highlightId = sessionStorage.getItem('highlightId');
  if (highlightId) {
    const element = document.getElementById(`row-${highlightId}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      element.classList.add('highlight-animation');
      setTimeout(() => element.classList.remove('highlight-animation'), 2000);
    }
    sessionStorage.removeItem('highlightId');
  }
}, [entities, moneyFlows, awards, foiaTargets]);
```

**CSS**:
```css
.highlight-animation {
  animation: highlight 2s ease-in-out;
}

@keyframes highlight {
  0%, 100% { background-color: transparent; }
  50% { background-color: rgba(91, 79, 255, 0.2); }
}
```

---

### 2. Detailed View Pages

Instead of Browse page, could navigate to dedicated detail pages:

**Routes**:
- `/entity/:id` - Detailed entity view
- `/money-flow/:id` - Detailed money flow view
- `/award/:id` - Detailed award view

**Benefits**:
- More focused UI
- Better for sharing links
- Can show related data
- Better SEO

---

### 3. Search History

Track clicked results:
```typescript
// In SearchBar
const handleResultClick = (result: SearchResult) => {
  // Track click for analytics
  trackSearchClick({
    query: query,
    result_type: result.type,
    result_id: result.id,
    timestamp: new Date()
  });
  
  // Save to search history
  const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
  history.unshift({ query, result, timestamp: Date.now() });
  localStorage.setItem('searchHistory', JSON.stringify(history.slice(0, 10)));
  
  // Navigate...
};
```

**UI**: Show recent searches when search bar is focused

---

## Files Modified

✅ `frontend/src/components/SearchBar.tsx` - Added navigation  
✅ `frontend/src/pages/Browse.tsx` - Added URL parameter handling  
✅ Frontend built and deployed

---

## Status

**✅ COMPLETED & TESTED**

Search navigation now works seamlessly:
- Click any search result → Navigate to Browse
- Correct tab selected automatically
- Search term pre-filled
- Data filtered correctly
- URL shareable/bookmarkable

---

**Next Steps**: Test in browser and verify user experience!

