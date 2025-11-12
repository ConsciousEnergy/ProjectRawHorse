# UI Components & Design System

**Date:** 2025-11-11  
**Status:** Active  
**Category:** Design

Complete reference for Project RawHorse UI components and design decisions.

---

## 🎨 Design Philosophy

**Goals:**
- Clean, modern interface
- Professional but approachable
- Data-focused (minimize chrome)
- Accessible (light/dark mode)
- Responsive (works on all screens)

**Inspiration:**
- Purple & Gold from PRHLogo
- Modern data dashboards
- Government transparency sites

---

## 🎨 Theme System

### Light Mode
```css
--primary-color: #5B4FFF;        /* Purple */
--accent-color: #FFD700;         /* Gold */
--background: #ffffff;
--surface: #f5f5f5;
--text: #1a1a1a;
--text-secondary: #666666;
--border: #e0e0e0;
```

### Dark Mode
```css
--primary-color: #7B6FFF;        /* Lighter purple */
--accent-color: #FFD700;         /* Gold (same) */
--background: #1a1a1a;
--surface: #2d2d2d;
--text: #ffffff;
--text-secondary: #b0b0b0;
--border: #404040;
```

### Implementation
**File:** `frontend/src/styles/theme.css`

Uses CSS custom properties with `[data-theme]` attribute:
```css
[data-theme="light"] { /* light theme vars */ }
[data-theme="dark"] { /* dark theme vars */ }
```

---

## 🧩 Core Components

### 1. ThemeToggle
**File:** `frontend/src/components/ThemeToggle.tsx`

**Features:**
- Sun/Moon icon toggle
- Smooth transitions
- LocalStorage persistence
- Accessible (aria-label)

**Usage:**
```tsx
import ThemeToggle from './components/ThemeToggle';
<ThemeToggle />
```

---

### 2. LegalDisclaimer
**File:** `frontend/src/components/LegalDisclaimer.tsx`

**Features:**
- Modal overlay
- Terms and conditions
- License information
- Data responsibility warnings
- Dismissible on acceptance

**Props:**
```typescript
interface LegalDisclaimerProps {
  onAccept: () => void;
}
```

---

## 📄 Page Components

### Dashboard
**File:** `frontend/src/pages/Dashboard.tsx`

**Layout:**
```
┌─────────────────────────────────┐
│  Dashboard Title                │
├───────┬───────┬───────┬─────────┤
│ Stat1 │ Stat2 │ Stat3 │ Stat4  │
├───────┼───────┴───────┴─────────┤
│ Stat5 │ Stat6                   │
├───────────────────────────────────┤
│  Welcome Card                   │
├─────────────────────────────────┤
│  Data Sources Card              │
└─────────────────────────────────┘
```

**Stat Cards:**
- Total Entities
- Money Flows
- Federal Awards
- FOIA Targets
- Total Spending (compact: $33.29M)
- Date Range (compact: 2004 - 2023)

---

### Browse
**File:** `frontend/src/pages/Browse.tsx`

**Features:**
- Tabbed interface (Entities, Money Flows, Awards, FOIA)
- Data tables with pagination
- Search and filters
- Loading states

---

### Contribute
**File:** `frontend/src/pages/Contribute.tsx`

**Layout:**
```
┌─────────────────────────────────┐
│  GitHub Token Setup             │
├─────────────────────────────────┤
│  [ Entity | Money Flow |        │
│    Award  | FOIA Target ]       │
├─────────────────────────────────┤
│  Form Fields                    │
│  (Dynamic based on type)        │
├─────────────────────────────────┤
│  Contributor Info (Optional)    │
├─────────────────────────────────┤
│  [Submit Contribution]          │
└─────────────────────────────────┘
```

**4 Contribution Types:**
1. Entity
2. Money Flow
3. Award
4. FOIA Target

---

## 🎨 Component Patterns

### Card Pattern
```tsx
<div className="card">
  <h3>Title</h3>
  <p>Content</p>
</div>
```

**Styles:**
- Rounded corners (8px)
- Subtle shadow
- Padding (20px)
- Background: surface color
- Border: 1px solid border color

---

### Stat Card Pattern
```tsx
<div className="stat-card">
  <h4>Label</h4>
  <p className="value">Value</p>
</div>
```

**Styles:**
- Larger value text (2rem)
- Primary color for value
- Centered alignment
- Hover effect (subtle scale)

---

### Tab Pattern
```tsx
<div className="tabs">
  <button className="active">Tab 1</button>
  <button>Tab 2</button>
</div>
```

**Styles:**
- Active tab: primary color background
- Inactive: surface color
- Smooth transitions
- Border bottom indicator

---

### Input Group Pattern
```tsx
<div className="input-group">
  <label>Label</label>
  <input type="text" />
</div>
```

**Styles:**
- Label above input
- Full width inputs
- Border on focus (primary color)
- Padding (10px)
- Margin bottom (15px)

---

## 🎯 Layout System

### Sidebar Navigation
**Width:** 250px (fixed)  
**Items:**
- Dashboard
- Browse
- Analysis
- Export
- Contribute
- About

**Active State:**
- Primary color background
- Bold text
- Icon + label

---

### Main Content Area
**Width:** calc(100% - 250px)  
**Padding:** 20px  
**Max Width:** None (fluid)

---

### Page Header
```tsx
<div className="page-header">
  <h2>Page Title</h2>
  <p>Description</p>
</div>
```

**Styles:**
- Margin bottom (30px)
- Title: 2rem
- Description: secondary text color

---

## 📱 Responsive Design

### Breakpoints
- **Desktop:** > 1024px (default)
- **Tablet:** 768px - 1024px
- **Mobile:** < 768px

### Mobile Adaptations
- Sidebar collapses to hamburger menu
- Stat grid: 2 columns on mobile
- Tables: horizontal scroll
- Cards: full width

---

## 🎨 Typography

### Font Family
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
  'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
```

### Font Sizes
- **h1:** 2.5rem (40px)
- **h2:** 2rem (32px)
- **h3:** 1.5rem (24px)
- **h4:** 1.25rem (20px)
- **body:** 1rem (16px)
- **small:** 0.875rem (14px)

### Font Weights
- **Normal:** 400
- **Medium:** 500
- **Bold:** 700

---

## 🎨 Color Usage

### Primary Color (Purple)
- Call-to-action buttons
- Active navigation items
- Links
- Important badges
- Value numbers

### Accent Color (Gold)
- Hover states
- Highlights
- Special badges
- Warning indicators

### Semantic Colors
- **Success:** #5afa5a
- **Error:** #fa5a5a
- **Warning:** #FFD700
- **Info:** #5B4FFF

---

## 🎨 Icons

### Library: Lucide React
**Package:** `lucide-react`

**Icons Used:**
- **Home:** Dashboard
- **Database:** Browse data
- **BarChart3:** Analysis
- **FileDown:** Export
- **Upload:** Contribute
- **Info:** About
- **Sun/Moon:** Theme toggle

**Style:**
- Size: 20px default
- Stroke width: 2
- Inline with text (vertical-align: middle)

---

## 🎨 Spacing System

### Scale (based on 8px)
- **xs:** 4px (0.25rem)
- **sm:** 8px (0.5rem)
- **md:** 16px (1rem)
- **lg:** 24px (1.5rem)
- **xl:** 32px (2rem)
- **2xl:** 48px (3rem)

---

## 🎨 Animation & Transitions

### Standard Transition
```css
transition: all 0.3s ease;
```

### Hover Effects
- Scale: 1.02
- Opacity: 0.9
- Background lighten/darken

### Theme Transition
```css
.theme-transitioning * {
  transition: background-color 0.3s ease,
              color 0.3s ease,
              border-color 0.3s ease !important;
}
```

---

## 🎨 Accessibility

### Color Contrast
- Light mode: WCAG AA compliant
- Dark mode: WCAG AA compliant
- Text on primary: white (high contrast)

### Keyboard Navigation
- All interactive elements focusable
- Tab order logical
- Focus indicators visible

### Screen Readers
- Semantic HTML
- ARIA labels where needed
- Alt text for images/icons

---

## 🎨 Component States

### Button States
- **Default:** Primary color, white text
- **Hover:** Accent color
- **Active:** Darker shade
- **Disabled:** Gray, reduced opacity
- **Loading:** Spinner + "Loading..."

### Input States
- **Default:** Border color
- **Focus:** Primary color border
- **Error:** Error color border
- **Disabled:** Gray background

---

## 🎨 Best Practices

1. **Use CSS variables** for colors (enables theming)
2. **Consistent spacing** (use spacing scale)
3. **Semantic HTML** (proper heading hierarchy)
4. **Mobile-first** (then enhance for desktop)
5. **Accessible** (keyboard + screen reader)
6. **Loading states** (show user feedback)
7. **Error handling** (clear error messages)

---

## 📚 Related Documentation

- **Colors:** [design/COLORS.md](COLORS.md)
- **PRD:** [../PRD.md](../PRD.md)
- **Features:** [../development/FEATURES.md](../development/FEATURES.md)

---

**Status:** ✅ Design System Established

All components follow consistent patterns and theming.

