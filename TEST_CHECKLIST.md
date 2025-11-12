# Project RawHorse - Testing Checklist

**Date:** 2025-11-11  
**Version:** v0.1.1-alpha (testing for v0.1.2)  
**Status:** In Progress

---

## 🎯 Test Objectives

1. Verify all pages load correctly
2. Test data displays properly
3. Test all features work end-to-end
4. Check for errors in console/logs
5. Validate contribution system

---

## ✅ Page Testing

### Dashboard (http://localhost:8000/)
- [ ] Page loads without errors
- [ ] All 6 stat cards display:
  - [ ] Total Entities (should show 9)
  - [ ] Money Flows (should show 28)
  - [ ] Federal Awards (should show 3)
  - [ ] FOIA Targets (should show 5)
  - [ ] Total Spending (should show $33.29M)
  - [ ] Date Range (should show 2004 - 2023)
- [ ] Welcome card displays
- [ ] Data sources card displays
- [ ] No console errors
- [ ] Light/dark mode toggle works

### Browse (http://localhost:8000/browse)
- [ ] Page loads without errors
- [ ] All 4 tabs are present:
  - [ ] Entities tab
  - [ ] Money Flows tab
  - [ ] Awards tab
  - [ ] FOIA Targets tab
- [ ] Entities table shows data (9 rows)
- [ ] Money Flows table shows data (28 rows)
- [ ] Awards table shows data (3 rows)
- [ ] FOIA Targets table shows data (5 rows)
- [ ] All columns display correctly
- [ ] No console errors

### Analysis (http://localhost:8000/analysis)
- [ ] Page loads without errors
- [ ] Tab navigation works
- [ ] Entity Graph section displays
- [ ] Money Flow Graph section displays
- [ ] Timeline section displays
- [ ] Placeholder text shows (visualizations not implemented yet)
- [ ] No console errors

### Export (http://localhost:8000/export)
- [ ] Page loads without errors
- [ ] All export format options visible:
  - [ ] CSV (Entities)
  - [ ] CSV (Money Flows)
  - [ ] CSV (Awards)
  - [ ] JSON
  - [ ] PDF Summary
- [ ] Can select an export format
- [ ] Export button is clickable
- [ ] No console errors

### Contribute (http://localhost:8000/contribute)
- [ ] Page loads without errors
- [ ] All 4 contribution type tabs present:
  - [ ] Entity
  - [ ] Money Flow
  - [ ] Award
  - [ ] FOIA Target
- [ ] GitHub token section displays
- [ ] Token validation works
- [ ] Entity form shows correct fields
- [ ] Money Flow form shows correct fields
- [ ] Award form shows correct fields
- [ ] FOIA Target form shows correct fields
- [ ] No console errors

### About (http://localhost:8000/about)
- [ ] Page loads without errors
- [ ] Project information displays
- [ ] License information shows
- [ ] Contact information displays
- [ ] No console errors

---

## 🔧 API Testing

### Health Check
```bash
curl http://localhost:8000/api/health
```
**Expected:** `{"status": "healthy"}`
- [ ] Returns 200 OK
- [ ] Returns expected JSON

### Data Endpoints
```bash
# Test entities
curl http://localhost:8000/api/data/entities

# Test money flows
curl http://localhost:8000/api/data/money-flows

# Test awards
curl http://localhost:8000/api/data/awards

# Test FOIA targets
curl http://localhost:8000/api/data/foia-targets

# Test stats
curl http://localhost:8000/api/data/stats
```
- [ ] `/api/data/entities` returns 9 entities
- [ ] `/api/data/money-flows` returns 28 flows
- [ ] `/api/data/awards` returns 3 awards
- [ ] `/api/data/foia-targets` returns 5 targets
- [ ] `/api/data/stats` returns correct statistics
- [ ] All return 200 OK
- [ ] All return valid JSON

### Export Endpoints
```bash
# Test CSV export
curl http://localhost:8000/api/export/csv/entities -o test_entities.csv

# Test JSON export
curl http://localhost:8000/api/export/json/entities -o test_entities.json
```
- [ ] CSV export works
- [ ] JSON export works
- [ ] Files are valid
- [ ] Data is complete

---

## 🤝 Contribution System Testing

### GitHub Token Validation
```bash
curl -H "X-GitHub-Token: YOUR_TOKEN" http://localhost:8000/api/contribute/validate-token
```
- [ ] With valid token: returns `{"valid": true}`
- [ ] With invalid token: returns `{"valid": false}`
- [ ] Without token: returns 401 error

### Entity Contribution
- [ ] Form accepts all required fields
- [ ] Validation works (required fields)
- [ ] Submit button works
- [ ] Success message displays
- [ ] PR URL is returned

### Money Flow Contribution
- [ ] Form accepts all required fields
- [ ] Validation works
- [ ] Submit works
- [ ] PR creation succeeds

### Award Contribution (NEW - Just Implemented!)
- [ ] Form accepts all required fields
- [ ] Validation works
- [ ] Submit works
- [ ] PR creation succeeds

### FOIA Target Contribution (NEW - Just Implemented!)
- [ ] Form accepts all required fields
- [ ] Validation works
- [ ] Submit works
- [ ] PR creation succeeds

---

## 🎨 UI/UX Testing

### Theme Toggle
- [ ] Light mode displays correctly
- [ ] Dark mode displays correctly
- [ ] Toggle button works
- [ ] Theme persists on page refresh
- [ ] Colors are correct (purple & gold)

### Navigation
- [ ] All sidebar links work
- [ ] Active page is highlighted
- [ ] Navigation is responsive
- [ ] Logo displays correctly

### Responsiveness
- [ ] Works on desktop (1920x1080)
- [ ] Works on laptop (1366x768)
- [ ] Works on tablet (768x1024)
- [ ] Works on mobile (375x667)

### Legal Disclaimer
- [ ] Disclaimer modal appears on first load
- [ ] Can accept disclaimer
- [ ] Doesn't appear again after acceptance
- [ ] Content is readable

---

## 🐛 Error Testing

### Console Errors
Check browser console (F12) for:
- [ ] No JavaScript errors
- [ ] No failed API calls
- [ ] No missing resources (404s)
- [ ] No CORS errors

### Backend Logs
Check terminal for:
- [ ] No Python errors
- [ ] All routes registered
- [ ] Database connected
- [ ] Data loaded correctly

### Edge Cases
- [ ] Empty search results handled
- [ ] Invalid form input handled
- [ ] Missing data handled gracefully
- [ ] Network errors caught

---

## 📊 Data Integrity Testing

### Database
- [ ] `data/prh.db` exists
- [ ] Database has 5 tables:
  - [ ] Entity (9 rows)
  - [ ] MoneyFlow (28 rows)
  - [ ] Award (3 rows)
  - [ ] FOIATarget (5 rows)
  - [ ] Relationship (15 rows)
- [ ] All foreign keys valid
- [ ] No duplicate records

### Data Loading
- [ ] All CSV files found
- [ ] No parsing errors
- [ ] All rows imported
- [ ] Data matches source files

---

## 🚀 Performance Testing

### Load Times
- [ ] Dashboard loads in < 2 seconds
- [ ] Browse page loads in < 2 seconds
- [ ] API responses < 500ms
- [ ] Export generates in < 5 seconds

### Resource Usage
- [ ] CPU usage reasonable (<50%)
- [ ] Memory usage reasonable (<500MB)
- [ ] No memory leaks
- [ ] Database queries efficient

---

## ✅ Integration Testing

### Complete User Flow 1: Browse Data
1. [ ] Open application
2. [ ] Accept disclaimer
3. [ ] Navigate to Browse
4. [ ] Switch between tabs
5. [ ] View all data types
6. [ ] No errors

### Complete User Flow 2: Export Data
1. [ ] Navigate to Export
2. [ ] Select CSV format
3. [ ] Click Export
4. [ ] File downloads
5. [ ] File is valid CSV
6. [ ] No errors

### Complete User Flow 3: Contribute (Mock)
1. [ ] Navigate to Contribute
2. [ ] Enter GitHub token
3. [ ] Validate token
4. [ ] Fill out entity form
5. [ ] Submit contribution
6. [ ] Receive success message
7. [ ] No errors

---

## 📝 Issues Found

### Critical Issues
*None yet - will document any found*

### Non-Critical Issues
*None yet - will document any found*

### Enhancement Ideas
*Any improvements identified during testing*

---

## 🎯 Test Results Summary

**Test Date:** 2025-11-11  
**Tester:** User + Claude  
**Version Tested:** v0.1.1-alpha (pre-v0.1.2)

**Pages Tested:** _ / 6  
**API Endpoints Tested:** _ / 17  
**Features Tested:** _ / 4 contribution types  
**Issues Found:** _  
**Overall Status:** ⏳ In Progress

---

## 📋 Next Steps After Testing

### If All Tests Pass ✅
1. Create v0.1.2-alpha release
2. Update release notes with "Complete contribution system"
3. Move to Option C (Network Visualization)

### If Issues Found ❌
1. Document all issues
2. Fix critical issues first
3. Re-test
4. Then proceed to release

---

## 🔍 How to Use This Checklist

1. **Run the application:** `.\RUN.bat`
2. **Open this checklist** side-by-side with browser
3. **Go through each section** systematically
4. **Check boxes** as you verify each item
5. **Document any issues** found
6. **Report results** when complete

---

**Testing Guide:**  
- ✅ = Working correctly  
- ❌ = Not working / error  
- ⚠️ = Works but has issues  
- ⏭️ = Skipped (not applicable)  
- ⏳ = In progress  

---

**Ready to test?** The application should be running at http://localhost:8000

Start with the Dashboard and work your way through each section! 🧪

