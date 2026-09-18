---
name: Hotelghino
description: A live trip-planning command center for tourist bookings — search, manage, and moderate stays through one confident, saturated product voice.
colors:
  ink: "#101a33"
  text: "#3a4257"
  muted: "#6b7387"
  line: "#e3e7f1"
  line-strong: "#cdd4e5"
  surface: "#ffffff"
  bg: "#f5f7fc"
  bg-tint: "#eef1fb"
  blue-50: "#eef2ff"
  blue-100: "#dbe3ff"
  blue-500: "#2a4fe0"
  blue-600: "#1f3fc4"
  blue-700: "#172f99"
  coral-50: "#fff1ec"
  coral-100: "#ffddd0"
  coral-500: "#ff6b4a"
  coral-600: "#e8542f"
  coral-700: "#c23f20"
  teal-50: "#e6faf6"
  teal-100: "#c7f3ea"
  teal-500: "#0db6a6"
  teal-600: "#0a9384"
  amber-50: "#fff7e6"
  amber-100: "#ffe9bd"
  amber-500: "#e2a327"
  amber-600: "#b9840f"
  red-50: "#fdecec"
  red-100: "#ffd6d6"
  red-500: "#e5484d"
  red-600: "#c23238"
typography:
  display:
    fontFamily: "Manrope, 'Segoe UI', system-ui, sans-serif"
    fontSize: "clamp(32px, 4.4vw, 52px)"
    fontWeight: 800
    lineHeight: 1.06
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Manrope, 'Segoe UI', system-ui, sans-serif"
    fontSize: "clamp(24px, 2.6vw, 30px)"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Manrope, 'Segoe UI', system-ui, sans-serif"
    fontSize: "19px"
    fontWeight: 700
    lineHeight: 1.25
  body:
    fontFamily: "Inter, 'Segoe UI', system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 450
    lineHeight: 1.6
  label:
    fontFamily: "Inter, 'Segoe UI', system-ui, sans-serif"
    fontSize: "13.5px"
    fontWeight: 700
rounded:
  sm: "10px"
  md: "16px"
  lg: "22px"
  full: "999px"
spacing:
  xs: "8px"
  sm: "14px"
  md: "20px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.blue-500}"
    textColor: "#ffffff"
    rounded: "{rounded.sm}"
    padding: "10px 20px"
  button-primary-hover:
    backgroundColor: "{colors.blue-600}"
  button-accent:
    backgroundColor: "{colors.coral-500}"
    textColor: "#ffffff"
    rounded: "{rounded.sm}"
    padding: "10px 20px"
  button-accent-hover:
    backgroundColor: "{colors.coral-600}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "10px 20px"
  button-danger:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.red-600}"
    rounded: "{rounded.sm}"
    padding: "10px 20px"
  card-hotel:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: "20px"
  status-pill:
    rounded: "{rounded.full}"
    padding: "5px 12px"
    typography: "{typography.label}"
---

# Design System: Hotelghino

## Overview

**Creative North Star: "The Live Command Center"**

Hotelghino reads as an operating console for tourist bookings, not a brochure: a committed indigo blue drives structure, navigation, and trust; a sunset coral fires only for conversion moments; a teal confirms availability and positive states. The system is unapologetically full-palette (four named roles: blue, coral, teal, amber, plus a red for danger/rejection) rather than a single muted brand color diluted across everything. It sits on a crisp near-white ground (`#f5f7fc`) with ink-navy text, so the saturation reads as confidence rather than noise.

The build rejects the flatter, corporate-blue-on-white SaaS template the product started from. Its energy shows up in three deliberate places rather than everywhere at once: the hero's animated gradient-mesh wash (indigo → coral → teal, drifting slowly), a floating glass-panel search card that breaks out of the hero's bottom edge, and a small set of overshoot-eased micro-accents (toast entrance, logo hover, timeline-icon hover, confirmation-icon pop-in). Everywhere else — management cards, tables, forms, status pills — the same tokens render as a calm, scannable console with no loud CTA competing with the task at hand.

Manrope (display/headings) is geometric and confident; Inter (body, UI, tables) is the dense-data workhorse. The pairing carries the "Airbnb/Booking-caliber product feel with its own identity" the team pinned for this build.

**Key Characteristics:**
- Full-palette strategy: indigo (primary/structure), coral (conversion CTAs only), teal (positive/availability), amber (pending), red (danger)
- Soft, offset, blurred elevation shadows (never hard/flat drop shadows) at generous 10–22px radii
- One animated gradient-mesh moment, reserved for the hero only — never repeated as page decoration
- `ease-out-expo` for all primary motion (reveals, hovers, panel transitions); `ease-out-back` reserved for four small secondary accents only
- Inline SVG iconography throughout — no icon fonts, no glyph icons

## Colors

The palette is saturated and role-driven: each hue has exactly one job, and none of them bleed into each other's territory.

### Primary
- **Committed Indigo** (`#2a4fe0`, `--blue-500`): navigation links (active/hover), primary buttons, focus rings' companion, table row hover tint, brand trust color. Darkens to `#1f3fc4` (`--blue-600`) on hover, `#172f99` (`--blue-700`) for link-hover text.

### Secondary
- **Sunset Coral** (`#ff6b4a`, `--coral-500`): the energy accent — reserved for conversion CTAs (`.button-accent`: "Registrar hotel", "Crear cuenta", "Ser propietario") and the nav's active-link underline. Never used for structural chrome. Darkens to `#e8542f` on hover.

### Tertiary
- **Teal** (`#0db6a6`, `--teal-500`): positive/active/availability signal — `status-pill--activo`, `status-pill--confirmada`, success toasts, success inline alerts. Darkens to `#0a9384` for text-on-tint use.

### Neutral
- **Ink Navy** (`#101a33`): headings, primary body-strong text, skip-link background.
- **Slate Text** (`#3a4257`): default body copy color.
- **Muted Slate** (`#6b7387`): secondary/meta text, placeholders, table headers.
- **Hairline** (`#e3e7f1`) / **Hairline Strong** (`#cdd4e5`): borders, dividers, dashed empty-state borders.
- **Surface White** (`#ffffff`): card and panel backgrounds.
- **Near-White Ground** (`#f5f7fc`) / **Tint** (`#eef1fb`): page background and subtle fills (table headers, empty-state icon backgrounds).

Two additional status roles complete the set: **Amber** (`#e2a327`) for pending/attention (`status-pill--pendiente`, with a soft pulsing ring animation), and **Red** (`#e5484d`) for danger/rejected/cancelled (`status-pill--rechazado`, `.button-danger`, error toasts and form-error boxes).

### Named Rules
**The One Accent Rule.** Coral fires for conversion actions only (primary CTAs, active-nav underline). It never appears as a structural or decorative color; structure and trust stay indigo.
**The Hero-Only Gradient Rule.** The animated indigo→coral→teal gradient-mesh wash is a single signature moment on the home hero background. It is not reused as a repeating pattern, card background, or section decoration anywhere else in the build.

## Typography

**Display Font:** Manrope (weights 500/600/700/800), with `"Segoe UI", system-ui, sans-serif` fallback
**Body Font:** Inter (weights 400/500/600/700), with the same system fallback

**Character:** Manrope's geometric, slightly condensed uppercase-capable letterforms carry confidence and brand voice in headings; Inter's neutral, highly legible forms carry the operational weight — dense tables, forms, and status text that Propietario/Administrador roles live in.

### Hierarchy
- **Display / H1** (800, `clamp(32px, 4.4vw, 52px)`, line-height 1.06, letter-spacing -0.02em): hero headline and page-level `<h1>`.
- **Headline / H2** (800, `clamp(24px, 2.6vw, 30px)`, line-height 1.15): section headings (`.section-heading`, `.management-header`).
- **Title / H3** (700, 19px, line-height 1.25): card and block titles (hotel names, "Habitaciones" block headers).
- **Body** (450, 16px base / 17.5px for auth copy, line-height 1.6, max-width 72ch): paragraph copy, muted-color by default.
- **Label** (700, 13.5px, uppercase not required): form labels in ink color; table headers use 12.5px, 700 weight, uppercase, 0.03em letter-spacing, muted color.

### Named Rules
**The Display-for-Structure Rule.** Manrope is reserved for headings, buttons, brand name, and status/label chrome (anything structural or action-bearing). Long-form and tabular content always renders in Inter.

## Layout

Content sits in a centered `min(1180px, calc(100% - 40px))` container (`.page`, `.app-header-inner`, `.app-footer-inner`) with a narrower `620px` variant (`.page-narrow`) for single-column forms. The hotel grid is a responsive 3-column grid (`repeat(3, minmax(0,1fr))`, 24px gap) that steps down to 2 columns at 1080px and 1 column at 780px. Auth screens use a two-column `minmax(0,1fr) minmax(380px,460px)` split (copy left, panel right) that collapses to a single stacked column at 1080px.

Spacing rhythm runs on an 8px-derived scale observed in the build: 8 / 14 / 16 / 20 / 24 / 32px for gaps and padding, with panels at 32px internal padding (22px on mobile ≤680px). The mobile nav becomes a fixed full-height slide-down panel below 780px; the header collapses to a hamburger toggle at that breakpoint too. `prefers-reduced-motion: reduce` disables all animation/transition durations globally (`0.001ms`) and the hero's drifting gradient specifically.

## Elevation & Depth

Hybrid: flat neutral surfaces at rest, lifted with soft offset-and-blurred shadows on cards, panels, toasts, and hover states — never hard-edged or zero-offset "glow" shadows. Shadows use the ink color at low opacity, never a saturated color-halo except for two named CTA-hover accents.

### Shadow Vocabulary
- **`--shadow-xs`** (`0 1px 2px rgba(16,26,51,0.06)`): sticky header's scrolled border companion.
- **`--shadow-sm`** (`0 6px 16px -4px rgba(16,26,51,0.10)`): resting hotel/management cards, status-pill-on-media, table-action hover.
- **`--shadow-md`** (`0 16px 34px -10px rgba(16,26,51,0.16)`): panels (auth, forms), toasts.
- **`--shadow-lg`** (`0 30px 60px -18px rgba(16,26,51,0.24)`): the floating hero search panel, hotel-card hover lift.
- **`--shadow-blue`** (`0 14px 28px -10px rgba(42,79,224,0.38)`): primary-button hover.
- **`--shadow-coral`** (`0 14px 28px -10px rgba(255,107,74,0.4)`): accent-button hover.

### Named Rules
**The Ambient-Not-Structural Rule.** Shadows communicate hover/rest state and stacking order (cards lifting on hover, panels floating over the hero), never a decorative outline. Color-tinted shadows (`--shadow-blue`, `--shadow-coral`) appear only on their matching button's hover state, not at rest.

## Shapes

Corners are consistently soft and generous, never sharp: `--radius-sm` (10px) for buttons, inputs, and table-wrap corners; `--radius-md` (16px) for cards and panels; `--radius-lg` (22px) for the hero container; `--radius-full` (999px) for pills, avatars, and the scrollbar thumb. Borders are thin (1–1.5px) hairlines in `--line`/`--line-strong`, used sparingly (secondary buttons, inputs, empty-state dashed borders) rather than as a primary structuring device — depth and grouping come from shadow and background-tint, not from outlines.

## Components

### Buttons
- **Shape:** `--radius-sm` (10px), min-height 44px (48px for `.button-full`), Manrope 700 weight, 14.5px.
- **Primary:** solid indigo (`#2a4fe0`) background, white text; hover darkens to `#1f3fc4` and adds `--shadow-blue`.
- **Accent:** solid coral (`#ff6b4a`) background, reserved for conversion actions ("Registrar hotel", "Crear cuenta"); hover darkens to `#e8542f` with `--shadow-coral`.
- **Secondary:** white background, `--line-strong` border, ink text; hover swaps border/text to indigo with `--shadow-sm`.
- **Danger:** white background, coral-adjacent red border/text; hover fills solid red (`#e5484d`) with white text.
- **All buttons:** `translateY(-2px)` lift on hover, a pointer-anchored white ripple on click (JS-driven, 650ms), `ease-out-expo` timing throughout.

### Cards / Containers
- **Corner Style:** `--radius-md` (16px), `overflow: hidden` on media cards.
- **Background:** white surface, `--line` 1px border.
- **Shadow Strategy:** `--shadow-sm` at rest, `--shadow-lg` + `translateY(-6px)` + border tint to `--blue-100` on hover (hotel-card only; management-card is static, no hover lift — it's a console element, not a discovery element).
- **Internal Padding:** 20px (hotel-card body), 26px (management-card, 22px on mobile).

### Status Pills
- **Style:** full-radius pill, 5px/12px padding, 12px/700-weight label text, a small `currentColor` dot before the text.
- **State roles:** teal (`activo`/`confirmada`), amber (`pendiente`, with a soft pulsing box-shadow ring), red (`rechazado`/`cancelada`). Each pairs a `-600` text tone with its matching `-50` tint background.

### Inputs / Fields
- **Style:** 1.5px `--line` border, `--radius-sm`, 46px min-height, white background.
- **Focus:** border shifts to indigo (`#2a4fe0`) with a 4px indigo-tint glow ring (`box-shadow: 0 0 0 4px var(--blue-50)`) — no color change on the label.
- **Error:** `.form-error-box` — red-tinted background (`--red-50`), red-600 text, entrance shake animation.

### Tables
- **Style:** header row uses `--bg-tint` background, muted uppercase 12.5px labels; body rows get a subtle indigo-tint hover (`--blue-50`); 1px `--line` row dividers, no divider on the last row.
- **Row actions:** compact pill-like links — indigo tint for "Modificar", red tint for "Eliminar" — lifting 1px on hover.

### Navigation
- Sticky, translucent-blurred header (`rgba(255,255,255,0.86)` + `blur(14px) saturate(1.4)`) that gains a hairline border and `--shadow-xs` once scrolled. Nav links get a coral underline that scales in from the left on hover (`ease-out-expo`, 260ms). Below 780px, the nav becomes a full-height slide-down panel triggered by a hamburger toggle that morphs into an X.

### Toasts (signature component)
Fixed top-right stack (bottom-full-width on mobile), white surface with `--shadow-md`, staggered `ease-out-back` entrance (a rare overshoot moment), auto-dismiss for success only after ~5.2s, manual close otherwise. Icon color/background matches the status role (teal/success, red/error-warning, blue/info).

## Do's and Don'ts

### Do:
- **Do** use indigo for all structural and navigational chrome; it is the only color allowed to carry trust/wayfinding weight.
- **Do** reserve coral strictly for conversion CTAs and the active-nav accent — never for card backgrounds, section washes, or decorative fills.
- **Do** use `ease-out-expo` (`cubic-bezier(0.16, 1, 0.3, 1)`) as the default transition timing for reveals, hovers, and panel motion.
- **Do** build depth with soft, offset, blurred shadows (`--shadow-sm/md/lg`) at the documented radii — never a hard-edged or zero-offset shadow.
- **Do** inline icons as SVG at 16–24px; the build has no icon-font or glyph-icon dependency anywhere.

### Don't:
- **Don't** repeat the hero's animated gradient-mesh wash as decoration elsewhere in the product; it is a one-time signature moment.
- **Don't** apply the `ease-out-back` overshoot easing outside its four confirmed accents (toast entrance, logo hover, timeline-icon hover, confirmation-icon pop-in); the primary motion grammar is `ease-out-expo`.
- **Don't** add kickers, eyebrows, or all-caps micro-labels above headings — none exist in the build; the hierarchy carries weight through Manrope size/weight alone.
- **Don't** introduce hard-offset, non-blurred "neobrutalist" shadows; every shadow token in this system is soft and blurred.
