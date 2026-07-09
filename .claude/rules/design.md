# Design — Plug N Play web

Bold & playful, teacher-facing. Confident display type, saturated brand
color blocks, thick navy borders + hard offset shadows, energetic flat
geometric shapes. Never AI-slop gradients or watercolor blobs.

## Stack
Next.js 16 (App Router, Server Components by default), React 19, Tailwind v4
(`@theme inline` in `app/globals.css`). Heed `web/AGENTS.md`: `<Image>` uses
`preload` (not the deprecated `priority`); new color tokens MUST be declared
under `@theme inline` to generate utilities.

## Tokens (`app/globals.css`)
- Brand: `--pnp-navy` #1a1f3d, `--pnp-blue` #3f42d9, `--pnp-teal` #2dd4bf
  (decorative only — fails AA for white text on a fill), `--pnp-orange`
  #f97316, `--pnp-yellow` #ffe25a, `--pnp-green` #22c55e.
- Accent (the single interactive accent): `--pnp-accent` #0d9488 (teal-600),
  `-hover` #0f766e, `-press` #115e59, `-soft` #ccfbf1. NEVER purple/indigo
  on interactive surfaces.
- Neutral ramp is COMPLETE: `pnp-gray-50…900`, including 400/600/800.
  Gotcha: using an undefined `pnp-*` token silently falls back to the
  inherited color (no error). Always confirm the shade exists in `@theme`.
- Fonts: `--font-heading` = Epilogue (display, 700–900), `--font-sans` =
  Inter (body). Use `font-heading` for headlines and bold labels.

## Components / patterns
- Buttons: ALWAYS `@/components/ui/Button` (tiers primary/secondary/
  tertiary). Never hand-roll button markup. One primary per view. The link
  variant accepts `onClick` for side-effects (e.g. closing the mobile menu).
  Comic depth: primary/secondary carry a 2px navy border + hard offset
  shadow `shadow-[3px_3px_0_var(--pnp-navy)]`; hover lifts up-left, press
  shifts down-right INTO the shadow (`active:translate-[3px,3px]
  active:shadow-none`). Tertiary stays flat (inline "View →" affordance).
- Metadata chips: `Tag` (neutral) / `Badge` (tinted by category, no purple
  tone). Standard codes use `Tag variant="code"`. Both carry the same comic
  depth as buttons — 2px navy border + hard offset shadow
  `shadow-[2px_2px_0_var(--pnp-navy)]` (smaller offset; non-interactive, no
  hover/press). Cards show the *format* ("Rich Task"/"Thin Slice"), not the
  internal task type.
- `Tile` (`@/components/ui/Tile`): the homepage jump-in card. White, 2px navy
  border, hard offset shadow `shadow-[4px_4px_0_var(--pnp-navy)]`, colored icon
  chip. `status="live"` → Link with hover-lift + focus ring; `status="soon"` →
  dashed, non-interactive, "Soon" chip.
- `Card` (`@/components/ui/Card`): the shared content-card envelope for
  strategies, tasks, units, and hub tiles — same navy border + hard offset
  shadow as Tile, optional `accent` top stripe. Pass `href` for the
  interactive (hover-lift + focus-ring) Link variant. Caller owns padding.
- `PageBanner` (`@/components/ui/PageBanner`): the one inner-page header.
  Sentence case, optional `back` link. `tone="navy"` (dark band — browse/detail
  pages) or `tone="light"` (white header — utility/form pages like generator).
  No eyebrow pill.
- Per-item color: cycle `BRAND_CYCLE` / `brandAccent(i)` from `lib/constants`
  (brand tokens only) — never hand-rolled hex like `#10b981`/`#ec4899`.
- Icons: lucide-style inline SVG only (`@/components/ui/icons`), 16–24px,
  `stroke="currentColor"`. No icon webfont.
- No decorative eyebrow pills above section headings (e.g. a "How it works"
  chip over an h2) — it reads as machine-generated; let the heading carry it.
  Functional micro-labels (nav, form fields, the canonical `SectionActionRow`
  "Build for {standard}" label) are fine.
- Section bands alternate light / saturated (blue product-peek, navy proof,
  yellow final-CTA) to build rhythm.

## Page structure
- Homepage (`app/page.tsx`): Hero (playground tile board) → ProductPeek (real
  featured task) → HowItWorks → Proof → FinalCTA. All Server Components except
  `Header`.
- Inner pages: `PageBanner` then content sections. Browse/detail (hub, units,
  library, rich-tasks) use `tone="navy"`; form/utility pages (generator,
  fluency) use `tone="light"`. Full-screen tools (whiteboard, flash-cards) get
  no banner — minimal chrome only.

## Motion & accessibility
- Motion is welcome but ALWAYS reduced-motion-safe: the global guard in
  `globals.css` neutralizes animations/transitions under
  `prefers-reduced-motion`. Decorative shapes/icons get `aria-hidden`.
- Never gate LCP content behind a JS animation (the old typewriter hero did —
  don't reintroduce it).
- AA contrast: white text only on accent/navy/blue fills (teal-600 = 4.51:1).
  Large display teal on near-white passes AA for large text only.
- One `<h1>` per page; sections use `<h2>`.

## Standing conventions
- Task library defaults to By Unit (unit-first); standards browse is secondary.
- ELA and Science are coming-soon pages (`app/ela`, `app/science`) until their
  content lands — never present them as live destinations without a "Soon"
  affordance.
