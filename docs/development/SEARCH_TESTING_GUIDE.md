# Search Feature - Testing Guide & Analytics

**Date**: November 30, 2025  
**Feature**: Advanced Search with Analytics  
**Purpose**: Test search functionality and track usage patterns

---

## 🧪 Testing Checklist

### Basic Search Tests

#### Test 1: Entity Search
**Search Query**: `Peraton`

**Expected Results**:
- ✅ Should find "Peraton" entity
- ✅ Should find money flows involving Peraton
- ✅ Should find awards to Peraton
- ✅ Results appear in < 1 second

**What to Verify**:
- Entity appears with "Corporation" type badge
- Related money flows show amounts
- Results are sorted by relevance

---

#### Test 2: Acronym Search
**Search Query**: `NGA`

**Expected Results**:
- ✅ Should find "NGA" entity (National Geospatial-Intelligence Agency)
- ✅ Should find money flows from/to NGA
- ✅ Should find FOIA targets for NGA
- ✅ Tooltip shows full name expansion

**What to Verify**:
- "Government Agency" type badge
- Gold color (#FFD700) in results
- Full name in description

---

#### Test 3: Partial Match
**Search Query**: `pera` (partial)

**Expected Results**:
- ✅ Should find "Peraton"
- ✅ Should find "Perspecta"
- ✅ Results still relevant

---

#### Test 4: Amount Search
**Search Query**: `223`

**Expected Results**:
- ✅ Should find money flows with $223M
- ✅ Should find awards with $223 in amount
- ✅ Amount displayed in results

---

#### Test 5: Multi-word Search
**Search Query**: `National Geospatial`

**Expected Results**:
- ✅ Should find NGA entity
- ✅ Matches both words
- ✅ High relevance score

---

### Advanced Search Tests

#### Test 6: Fuzzy Matching
**Search Queries**: 
- `Pereton` (typo)
- `vertas` (typo for Veritas)

**Expected Results**:
- ✅ Should still find correct entities
- ✅ Fuzzy matching tolerance works

---

#### Test 7: Case Insensitivity
**Search Queries**:
- `PERATON` (all caps)
- `peraton` (all lowercase)
- `PeRaToN` (mixed case)

**Expected Results**:
- ✅ All return same results
- ✅ Case doesn't matter

---

#### Test 8: Empty/Invalid Queries
**Search Queries**:
- ` ` (space only)
- `a` (single character)
- `xyz123abc` (nonsense)

**Expected Results**:
- ✅ Single character doesn't search (min 2)
- ✅ Nonsense shows "No results found"
- ✅ Helpful error messages

---

### UI/UX Tests

#### Test 9: Keyboard Navigation
**Steps**:
1. Press `/` to focus search
2. Type `peraton`
3. Press `↓` to navigate results
4. Press `Enter` to select

**Expected Results**:
- ✅ `/` focuses search input
- ✅ Arrow keys navigate (highlight moves)
- ✅ Enter selects highlighted result
- ✅ Visual feedback for selected item

---

#### Test 10: Loading States
**Steps**:
1. Type search query
2. Observe loading spinner

**Expected Results**:
- ✅ Spinner appears while loading
- ✅ Spinner disappears when results load
- ✅ No flickering or lag

---

#### Test 11: Close/Clear Behavior
**Steps**:
1. Search for something
2. Press `Esc` to close
3. Search again
4. Click X button to clear

**Expected Results**:
- ✅ `Esc` closes results dropdown
- ✅ `X` button clears search input
- ✅ Dropdown closes on clear

---

#### Test 12: Click Outside
**Steps**:
1. Open search results
2. Click anywhere outside

**Expected Results**:
- ✅ Results dropdown closes
- ✅ Search input remains focused

---

### Performance Tests

#### Test 13: Rapid Typing
**Steps**:
1. Type very quickly: `peratonveritas`
2. Observe behavior

**Expected Results**:
- ✅ Debouncing works (only searches after 300ms pause)
- ✅ No excessive API calls
- ✅ Smooth performance

---

#### Test 14: Large Result Set
**Search Query**: `a` (would match many)
*Note: This won't search due to min 2 characters, try `an` instead*

**Expected Results**:
- ✅ Results limited to 20 (default limit)
- ✅ Fast response even with many matches
- ✅ UI handles many results gracefully

---

### Mobile/Responsive Tests

#### Test 15: Mobile View
**Steps**:
1. Resize browser to mobile width (< 768px)
2. Test search functionality

**Expected Results**:
- ✅ Search bar fits in sidebar
- ✅ Results dropdown responsive
- ✅ Touch interactions work
- ✅ Keyboard hints hidden on mobile

---

### Accessibility Tests

#### Test 16: Screen Reader
**Steps**:
1. Navigate with Tab key
2. Check ARIA labels

**Expected Results**:
- ✅ Search input is focusable
- ✅ Clear button has aria-label
- ✅ Results are announced
- ✅ Keyboard navigation works

---

## 📊 Search Analytics Tracking

### What We Track

1. **Search Query**: What users searched for
2. **Results Count**: How many results were found
3. **Timestamp**: When the search happened
4. **Response Time**: How fast the search was
5. **Query Type**: Auto-suggest vs full search

### Database Schema

```sql
CREATE TABLE search_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    results_count INTEGER,
    search_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    user_agent TEXT,
    ip_address TEXT
);
```

### Analytics Queries

**Most Popular Searches**:
```sql
SELECT query, COUNT(*) as search_count
FROM search_logs
WHERE query != ''
GROUP BY query
ORDER BY search_count DESC
LIMIT 20;
```

**Searches with No Results** (Areas to improve):
```sql
SELECT query, COUNT(*) as attempt_count
FROM search_logs
WHERE results_count = 0
GROUP BY query
ORDER BY attempt_count DESC
LIMIT 20;
```

**Average Response Time**:
```sql
SELECT AVG(response_time_ms) as avg_ms,
       MIN(response_time_ms) as min_ms,
       MAX(response_time_ms) as max_ms
FROM search_logs;
```

**Search Activity by Hour**:
```sql
SELECT strftime('%H', search_timestamp) as hour,
       COUNT(*) as searches
FROM search_logs
GROUP BY hour
ORDER BY hour;
```

---

## 🎯 Testing Results Template

**Date**: _____________  
**Tester**: _____________

| Test # | Feature | Status | Notes |
|--------|---------|--------|-------|
| 1 | Entity Search | ☐ Pass ☐ Fail | |
| 2 | Acronym Search | ☐ Pass ☐ Fail | |
| 3 | Partial Match | ☐ Pass ☐ Fail | |
| 4 | Amount Search | ☐ Pass ☐ Fail | |
| 5 | Multi-word | ☐ Pass ☐ Fail | |
| 6 | Fuzzy Matching | ☐ Pass ☐ Fail | |
| 7 | Case Insensitive | ☐ Pass ☐ Fail | |
| 8 | Empty/Invalid | ☐ Pass ☐ Fail | |
| 9 | Keyboard Nav | ☐ Pass ☐ Fail | |
| 10 | Loading States | ☐ Pass ☐ Fail | |
| 11 | Close/Clear | ☐ Pass ☐ Fail | |
| 12 | Click Outside | ☐ Pass ☐ Fail | |
| 13 | Rapid Typing | ☐ Pass ☐ Fail | |
| 14 | Large Results | ☐ Pass ☐ Fail | |
| 15 | Mobile View | ☐ Pass ☐ Fail | |
| 16 | Accessibility | ☐ Pass ☐ Fail | |

**Overall Assessment**: ☐ Ready for Production ☐ Needs Work

**Issues Found**:
1. ___________________________________
2. ___________________________________
3. ___________________________________

---

## 💡 Insights from Analytics

### What to Look For

1. **Popular Entities**: Which organizations are users most interested in?
2. **Missing Data**: What searches return no results? (Add this data!)
3. **Search Patterns**: Do users search by name, amount, or acronym?
4. **Performance Issues**: Are any queries particularly slow?

### Action Items Based on Analytics

**If users search for X repeatedly with no results**:
→ Add X to the database

**If searches for acronyms are popular**:
→ Expand acronym dictionary in `AGENCY_ACRONYMS`

**If amount searches are common**:
→ Consider adding amount range filters

**If response time > 1 second**:
→ Add database indexes or optimize queries

---

## 🔧 Quick Test Commands

### Test Backend API Directly

```bash
# Test search endpoint
curl "http://127.0.0.1:8000/api/search?q=peraton"

# Test with type filter
curl "http://127.0.0.1:8000/api/search?q=nga&types=entities&types=money_flows"

# Test with limit
curl "http://127.0.0.1:8000/api/search?q=a&limit=5"
```

### View Search Logs

```bash
# Connect to database
sqlite3 data/prh.db

# View recent searches
SELECT * FROM search_logs ORDER BY search_timestamp DESC LIMIT 10;

# Popular searches
SELECT query, COUNT(*) FROM search_logs GROUP BY query ORDER BY COUNT(*) DESC LIMIT 10;
```

---

**Ready to test!** Open http://127.0.0.1:8000 and start searching! 🚀

