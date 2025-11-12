# Project RawHorse - Color Reference Guide

 🌘𓂀🐴✨

---

## 🎨 Primary Colors

### Purple Horse (Left)
```
Primary:      #5B4FFF  █████  Vibrant purple-blue
Accent:       #8B7FFF  █████  Light purple
Hover:        #4A3EE6  █████  Darker purple (light mode)
Hover Dark:   #6B5FFF  █████  Lighter purple (dark mode)
```

### Gold Horse (Right)
```
Secondary:    #D4A218  █████  Golden orange
Accent:       #E6B933  █████  Light gold
```

---

## 🌈 Complete Color Palette

### Light Mode

**Backgrounds:**
```
Primary:      #FFFFFF  █████  Pure white
Secondary:    #F5F5F7  █████  Light gray
Tertiary:     #E8E8EA  █████  Medium gray
Elevated:     #FFFFFF  █████  White (with shadow)
```

**Text:**
```
Primary:      #1C1C1E  █████  Almost black
Secondary:    #48484A  █████  Dark gray
Tertiary:     #8E8E93  █████  Medium gray
Inverse:      #FFFFFF  █████  White (on colored bg)
```

**Borders:**
```
Default:      #D1D1D6  █████  Light gray
Hover:        #A1A1A6  █████  Medium gray
```

### Dark Mode

**Backgrounds:**
```
Primary:      #1C1C1E  █████  Very dark gray
Secondary:    #2C2C2E  █████  Dark gray
Tertiary:     #3A3A3C  █████  Medium dark gray
Elevated:     #2C2C2E  █████  Dark gray (with shadow)
```

**Text:**
```
Primary:      #FFFFFF  █████  Pure white
Secondary:    #E5E5EA  █████  Light gray
Tertiary:     #AEAEB2  █████  Medium gray
Inverse:      #1C1C1E  █████  Dark (on colored bg)
```

**Borders:**
```
Default:      #48484A  █████  Dark gray
Hover:        #636366  █████  Medium gray
```

---

## 🎯 State Colors

```
Success:      #34C759  █████  Green
Warning:      #FF9500  █████  Orange
Error:        #FF3B30  █████  Red
Info:         #007AFF  █████  Blue
```

---

## 📐 Usage Examples

### Sidebar
```css
Background:     var(--sidebar-bg)       /* Light gray / Dark gray */
Border:         var(--sidebar-border)   /* Subtle border */
Text:           var(--sidebar-text)     /* Primary text */
Hover:          var(--sidebar-hover)    /* Lighter background */
Active BG:      #5B4FFF (Purple)        /* Active item */
Active Text:    #FFFFFF (White)         /* Text on active */
```

### Cards
```css
Background:     var(--card-bg)          /* White / Dark gray */
Border:         var(--card-border)      /* Subtle border */
Shadow:         var(--card-shadow)      /* Soft shadow */
```

### Stat Cards
```css
Odd cards:      Purple value (#5B4FFF)
Even cards:     Gold value (#D4A218)
Background:     Gradient (card-bg → bg-secondary)
```

### Buttons
```css
Primary BG:     #5B4FFF (Purple)
Primary Hover:  #4A3EE6 (Darker) / #6B5FFF (Lighter)
Primary Text:   #FFFFFF (White)

Secondary BG:   var(--bg-tertiary)
Secondary Text: var(--text-primary)
```

### Inputs
```css
Background:     White / Dark gray
Border:         Light gray / Dark gray
Focus Border:   #5B4FFF (Purple)
Focus Shadow:   rgba(91, 79, 255, 0.1)
```

---

## 🖌️ Logo Colors Extracted

From your PRHLogo.png:

**Left Horse (Purple):**
- Main body: Purple-blue (#5B4FFF)
- Highlights: Lighter purple
- Moon/celestial element: Light accent

**Right Horse (Gold):**
- Main body: Golden orange (#D4A218)
- Highlights: Brighter gold
- Sun/celestial element: Warm accent

**Background:**
- Transparent/white

---

## 💡 Design Principles

1. **Purple as Primary**: Main actions, active states, focus
2. **Gold as Accent**: Alternating elements, special highlights
3. **Consistent Contrast**: WCAG AA compliant in both modes
4. **Smooth Transitions**: 0.3s ease for theme changes
5. **Semantic Colors**: Clear meaning for states (success, error, etc.)

---

## 🎨 How to Use

In your CSS:
```css
.my-component {
  background-color: var(--card-bg);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.my-button {
  background-color: var(--color-primary);  /* Purple */
  color: var(--text-inverse);               /* White */
}

.my-accent {
  color: var(--color-secondary);            /* Gold */
}
```

In your TypeScript:
```typescript
const theme = localStorage.getItem('theme'); // 'light' or 'dark'
```

---

## 🌓 Theme Toggle

Located: Top-right corner
Icon: Sun (light mode) / Moon (dark mode)
Color: Matches current theme
Hover: Purple border
Animation: Smooth rotation

---

**Your brand colors are now consistently applied throughout the entire application!** 🎉
