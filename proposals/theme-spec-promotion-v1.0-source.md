# Thingalog Theme Specification v1.0

## Overview

A Thingalog theme controls the visual presentation of a catalog across all view modes: browse, detail, kiosk, embed, and print. Themes are JSON objects that map to CSS custom properties, layout rules, and component variants.

The catdef standard defines the *shape* of a theme (colors, fonts, mode). This document defines how the Thingalog renderer *consumes* that shape — every CSS variable, every layout breakpoint, every component variant, every animation.

Third parties can build Thingalog-compatible themes using this spec. The spec is published; the renderer is proprietary.

## Architecture

A theme flows through three layers:

1. **catdef theme object** → declares intent (accent color, mode, font)
2. **Thingalog theme resolver** → fills defaults, validates, computes derived values (accent-dim from accent, contrast ratios, shadow depths)
3. **CSS custom properties** → applied to the DOM, consumed by components

The renderer never reads the catdef theme directly. It always goes through the resolver, which guarantees every variable has a value.

## CSS Custom Properties

### Colors

| Variable | Default (light) | Default (dark) | Description |
|----------|-----------------|----------------|-------------|
| `--accent` | `#6366f1` | `#818cf8` | Primary brand color. Buttons, links, active states |
| `--accent-hover` | computed | computed | Accent darkened 10% (light) or lightened 10% (dark) |
| `--accent-dim` | computed | computed | Accent at 15% opacity. Backgrounds, badges |
| `--accent-contrast` | `#ffffff` | `#000000` | Text color on accent backgrounds (auto-computed for WCAG AA) |
| `--bg` | `#f8fafc` | `#0d1117` | Page background |
| `--bg-raised` | `#ffffff` | `#161b22` | Cards, modals, dropdowns — one step above bg |
| `--bg-sunken` | `#f1f5f9` | `#010409` | Inputs, search bar — one step below bg |
| `--ink` | `#1e293b` | `#e6edf3` | Primary text |
| `--ink-secondary` | `#475569` | `#8b949e` | Secondary text, labels |
| `--ink-tertiary` | `#94a3b8` | `#484f58` | Placeholder text, disabled states |
| `--panel` | `#ffffff` | `#161b22` | Card and panel backgrounds |
| `--muted` | `#64748b` | `#8b949e` | De-emphasized text |
| `--border` | `#e2e8f0` | `#30363d` | Borders, dividers |
| `--border-strong` | `#cbd5e1` | `#484f58` | Emphasized borders (focus, hover) |
| `--danger` | `#ef4444` | `#f87171` | Delete, error, destructive actions |
| `--danger-dim` | computed | computed | Danger at 15% opacity |
| `--success` | `#22c55e` | `#4ade80` | Success, saved, positive states |
| `--warning` | `#f59e0b` | `#fbbf24` | Warning, attention states |
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | `0 1px 2px rgba(0,0,0,0.3)` | Subtle elevation |
| `--shadow-md` | `0 4px 12px rgba(0,0,0,0.08)` | `0 4px 12px rgba(0,0,0,0.4)` | Card hover, dropdowns |
| `--shadow-lg` | `0 12px 32px rgba(0,0,0,0.12)` | `0 12px 32px rgba(0,0,0,0.5)` | Modals, overlays |

### Typography

| Variable | Default | Description |
|----------|---------|-------------|
| `--font-family` | `-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif` | Base font stack |
| `--font-family-mono` | `'SF Mono', Monaco, 'Cascadia Code', monospace` | Monospace (IDs, codes) |
| `--font-size-xs` | `11px` | Chip labels, fine print |
| `--font-size-sm` | `13px` | Secondary text, metadata |
| `--font-size-base` | `14px` | Body text, field values |
| `--font-size-lg` | `16px` | Subheadings, card titles |
| `--font-size-xl` | `20px` | Page titles |
| `--font-size-2xl` | `28px` | Hero titles (kiosk mode) |
| `--font-size-3xl` | `40px` | Kiosk item title |
| `--font-weight-normal` | `400` | Body text |
| `--font-weight-medium` | `500` | Labels, emphasis |
| `--font-weight-bold` | `700` | Titles, headings |
| `--line-height` | `1.5` | Base line height |
| `--line-height-tight` | `1.25` | Headings |

### Spacing and Layout

| Variable | Default | Description |
|----------|---------|-------------|
| `--radius-sm` | `4px` | Chips, small elements |
| `--radius-md` | `8px` | Inputs, buttons |
| `--radius-lg` | `12px` | Cards |
| `--radius-xl` | `16px` | Modals, panels |
| `--radius-full` | `9999px` | Pill shapes, avatars |
| `--spacing-xs` | `4px` | Tight gaps |
| `--spacing-sm` | `8px` | Compact spacing |
| `--spacing-md` | `12px` | Default spacing |
| `--spacing-lg` | `16px` | Section spacing |
| `--spacing-xl` | `24px` | Major section gaps |
| `--spacing-2xl` | `40px` | Page-level padding |
| `--header-height` | `56px` | Sticky header height |
| `--toolbar-height` | `48px` | Sticky toolbar height |
| `--card-min-width` | `260px` | Grid card minimum |
| `--card-aspect` | `4/3` | Card image aspect ratio |
| `--modal-max-width` | `640px` | Detail modal width |
| `--kiosk-info-height` | `20vh` | Kiosk info strip height |

### Transitions

| Variable | Default | Description |
|----------|---------|-------------|
| `--transition-fast` | `0.15s ease` | Hover, focus states |
| `--transition-base` | `0.2s ease` | Panel open/close |
| `--transition-slow` | `0.4s ease` | Modal, kiosk rotation |
| `--transition-kiosk` | `1s ease-in-out` | Kiosk fade between items |

## Components

Each component reads from the CSS variables above. Themes control appearance entirely through variables — no component-level CSS overrides needed.

### Header
- Background: `--ink` (inverted), text: `--bg`
- Height: `--header-height`
- Logo/name left-aligned, stats right-aligned
- Sticky at viewport top

### Toolbar
- Background: `--panel`, border-bottom: `--border`
- Search input: `--bg-sunken` background, `--border` border
- Sort/filter controls: `--bg-sunken` background
- Sticky below header

### Card Grid
- CSS Grid: `repeat(auto-fill, minmax(var(--card-min-width), 1fr))`
- Gap: `--spacing-lg`
- Padding: `--spacing-xl`

### Card
- Background: `--panel`, border: `--border`, radius: `--radius-lg`
- Hover: `--shadow-md`, slight scale (1.01)
- Image area: aspect-ratio `--card-aspect`, fallback: `--bg-sunken` with icon
- Title: `--font-size-lg`, `--font-weight-bold`
- Subtitle: `--font-size-sm`, `--muted`
- Chip row: `--font-size-xs`, `--bg-sunken` background, `--radius-sm`

### Detail Modal
- Overlay: black at 50% opacity
- Panel: `--bg-raised`, radius: `--radius-xl`, max-width: `--modal-max-width`
- Shadow: `--shadow-lg`
- Field label: `--font-size-xs`, `--ink-tertiary`, uppercase, letter-spacing 0.05em
- Field value: `--font-size-base`, `--ink`
- Enumerated chips: `--bg-sunken`, border `--border`, radius `--radius-full`

### Kiosk View
- Full viewport, no scroll
- Photo: covers viewport (object-fit: cover) or fills `--kiosk-info-height` remainder
- Info strip: `--bg` with slight transparency (backdrop-filter: blur)
- Title: `--font-size-3xl`, `--font-weight-bold`
- Fields: `--font-size-xl`, arranged in columns
- QR code: bottom-right corner, white background pad
- Transition between items: `--transition-kiosk`

### Empty State
- Centered vertically
- Icon: 48px, `--muted`
- Message: `--font-size-lg`, `--ink-secondary`
- Sub-message: `--font-size-sm`, `--muted`

## Responsive Breakpoints

| Breakpoint | Width | Behavior |
|------------|-------|----------|
| `mobile` | < 640px | Single column grid, full-width cards, bottom sheet modal |
| `tablet` | 640–1024px | 2-column grid, side panel modal |
| `desktop` | > 1024px | 3+ column grid, centered modal |
| `kiosk` | any | Full viewport, no breakpoint behavior |

## Theme JSON Shape

The catdef theme object is the input. The Thingalog resolver expands it:

```json
{
  "theme": {
    "accent": "#8b4513",
    "bg": "#faf6ef",
    "panel": "#fffaf2",
    "ink": "#2d1810",
    "muted": "#8b7355",
    "border": "#e8dcc8",
    "font": "Georgia, 'Times New Roman', serif",
    "card_radius": "8px",
    "card_aspect": "1/1",
    "mode": "light"
  }
}
```

The resolver:
1. Applies `mode` defaults for any missing color
2. Computes `accent-hover`, `accent-dim`, `accent-contrast` from `accent`
3. Computes `danger-dim` from `danger`
4. Computes shadows scaled to mode (lighter in light, deeper in dark)
5. Maps `font` → `--font-family`
6. Maps `card_radius` → `--radius-lg`
7. Maps `card_aspect` → `--card-aspect`
8. Sets all CSS custom properties on `:root`

Any property not specified in the theme JSON gets the mode default.

## Built-in Themes

Thingalog ships with a set of curated themes. Each is a complete theme JSON that can be referenced by name in the catdef:

```json
{"theme": "Museum"}
```

| Name | Description | Mode | Accent |
|------|-------------|------|--------|
| `Default` | Clean, neutral, professional | light | indigo |
| `Midnight` | Deep dark, high contrast | dark | blue |
| `Museum` | Warm, elegant, gallery-like | light | saddle brown |
| `Gallery` | Minimal white, photos first | light | slate |
| `Brutalist` | High contrast, no curves, bold | light | black |
| `Moss` | Earthy, natural, warm greens | light | forest green |
| `Neon` | Dark with vivid accent pops | dark | electric pink |
| `Paper` | Warm off-white, serif type | light | dark brown |
| `Nordic` | Cool grays, clean, airy | light | steel blue |
| `Terracotta` | Warm clay tones, textured feel | light | burnt orange |

## Accessibility Requirements

All themes MUST meet WCAG 2.1 AA contrast ratios:
- Normal text (`--ink` on `--bg`): minimum 4.5:1
- Large text (`--font-size-xl`+): minimum 3:1
- Interactive elements (`--accent` on `--bg`): minimum 4.5:1
- Focus indicators: 3:1 against adjacent colors

The resolver validates contrast ratios and adjusts computed colors if necessary. A theme that specifies `accent: "#ffff00"` on `bg: "#ffffff"` will have its accent darkened automatically to meet AA.

---

*Thingalog Theme Specification v1.0. April 2026.*
*Published by Thingalog. Third-party theme development encouraged.*
