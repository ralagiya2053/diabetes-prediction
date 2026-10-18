# Plan 01 — Website UI: Full page redesign to match Figma

**Status:** Draft
**Feature ID:** F1
**Branch:** feat/01-website-ui-links
**Spec:** specs/01-website-ui-links/spec.md
**Author:** Rushikesh Alagiya
**Created:** 2026-10-16

> This plan replaces the previous narrow-scope plan (nav + footer links only).
> It is written against the approved expanded spec (AC1–AC10).

## 1. Approach Summary
Rebuild `frontend/index.html` as semantic HTML — `header`, `main` (hero + form
card + disclaimer), `footer` — styled by a new external stylesheet, keeping the
existing form fields, Lambda payload, and submit/result JS logic functionally
identical (result/error block restyled only). Design tokens (colors, spacing,
type) come from the Figma design (Nodes 3:30, 3:112, page frame), pulled via
the Figma MCP at build time. Inter loads from Google Fonts with a `system-ui`
fallback. Responsive behavior: 1440px content cap, two-column form grid at
≥1024px, mobile adjustments at <768px.

## 2. Files to Create
- `frontend/assets/styles.css` — all new styles: tokens, reset, header, hero,
  form card, grid, hints, card footer, disclaimer, footer, responsive rules
- (Already present, will be committed as part of this feature: `frontend/assets/activity.svg`)

## 3. Files to Modify
- `frontend/index.html` — full restructure of markup: header, hero, form card
  wrapper, field pairing, inline hints, card footer row, disclaimer, page
  footer; `<link>` to Google Fonts (Inter) and `styles.css`; result/error block
  restyled. JS logic unchanged except selectors if class names change. No API
  or payload changes.
- Frozen files (`app/`, `Dockerfile`, model artifacts, `train/diabetes.csv`)
  are untouched — no conflict.

## 4. Architecture / Data Flow

```
User browser
  └─ GitHub Pages (static hosting)
       └─ frontend/index.html
            ├─ frontend/assets/styles.css      (presentation)
            ├─ frontend/assets/activity.svg    (header icon)
            ├─ Google Fonts: Inter             (with system-ui fallback)
            └─ <form> ──fetch POST──► Lambda Function URL  (frozen)
                                         └─ /predict (payload unchanged)
              result/error block → restyled, same content
```

- Header/footer/hero/card are pure static HTML + CSS; no new JS.
- The existing fetch-to-Lambda logic in `index.html` is preserved; only its
  display targets may be re-styled.

## 5. Step-by-Step Implementation

1. **Design context pull** — attempt Figma MCP to extract measurements/colors
   for Nodes 3:30, 3:112, and the page frame (hint placement per AC5, card
   max-width per AC3). If MCP is unavailable, proceed with the spec defaults
   (right-aligned suffix hints; 1440px cap per AC10). — enables AC3, AC5
2. **Base styles** — reset, CSS custom-property tokens (colors incl. off-white
   `#f7f8fa`, dark blue `#1e3a8a`, spacing), 1440px centered content cap,
   Inter loaded via Google Fonts with preconnect hints:
   `<link rel="preconnect" href="https://fonts.googleapis.com">`,
   `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>`,
   `<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">`,
   plus a `system-ui` fallback. — satisfies AC10
3. **Header** — `<header>`: 88px height, 64px horizontal padding, 38×38 blue
   tile with 22×22 `activity.svg`, product name left, "Health assessment"
   right; `<768px`: 24px padding, label hidden. — satisfies AC1
4. **Hero section** — eyebrow "A LITTLE INSIGHT. A FIRST STEP." (uppercase,
   letter-spaced), centered title, subtitle, verbatim from spec. — satisfies AC2
5. **Form card shell** — white rounded card, subtle border/shadow, heading
   "Your health details", subtext, "8 health indicators" badge with icon at
   top-right. — satisfies AC3
6. **Form grid** — two-column grid ≥1024px, single column below; pair fields
   Gender+Age, Hypertension+Heart disease, Smoking history+BMI, HbA1c+Blood
   glucose. — satisfies AC4
7. **Field hints** — unit/range hints per AC5 list, placement from Figma
   (fallback: right-aligned suffix inside input). — satisfies AC5
8. **Card footer row** — "Ready when you are" + subtext left; Predict button
   right: dark blue, white text, arrow icon. — satisfies AC6
9. **Disclaimer** — centered line below card with info icon, spec text
   verbatim. — satisfies AC7
10. **Page footer** — 92px height, 64px padding, branding left, nav links right
    in `#1e3a8a`, relative hrefs `privacy.html` / `terms.html` / `about.html`,
    same window; `<768px`: 24px padding. — satisfies AC8
11. **Result/error restyle** — restyle the existing result/error container to
    match the card design; verify payload to Lambda URL and displayed content
    are unchanged. — satisfies AC9
12. **Responsive + layout stability pass** — verify no horizontal scroll at any
    viewport ≥1024px, 1440px cap centered, single-column grid and 24px header/
    footer padding under 768px. — satisfies AC4, AC10

## 6. Test Strategy
- **Manual validation (per AC):**
  - AC1/AC8: measure header (88px) and footer (92px) heights + padding in
    devtools at 1024px and 1920px; re-check at 767px for 24px padding and
    hidden "Health assessment" label.
  - AC2/AC3/AC6/AC7: side-by-side visual comparison against the Figma frame;
    verify copy verbatim (eyebrow, subtitle, headings, badge, card footer text,
    disclaimer).
  - AC4: inspect grid at 1024px+ (two columns, correct pairs) and below
    (single column).
  - AC5: confirm each hint text renders (years, "0 = No · 1 = Yes", kg/m², %,
    mg/dL).
  - AC9: submit the form with a known input set; confirm identical request
    payload (Network tab) and same prediction/probability as before the
    redesign; trigger an error path and confirm content unchanged.
  - AC10: sweep viewport widths 1024→1920+ for horizontal scroll; confirm
    1440px centering and off-white background.
  - Footer links: click each — resolves to relative path in same tab (404 is
    expected until F2).
- **Automated tests:** none — F1 is static; CI HTML validation covers it.
- ACs 1–10 each map to the manual steps above (traceable to Steps 1–12,
  Section 5).

## 7. Rollout & Rollback
- **Rollout:** merge `feat/01-website-ui-links` → `main`; GitHub Pages
  automatically serves the updated `frontend/`. No Lambda or container changes,
  so no AWS deployment is involved.
- **Rollback:** `git revert` the merge commit on `main`; GitHub Pages rebuilds
  and restores the previous page. Because the change is purely frontend and
  additive to the repo, revert is clean.

## 8. Risks & Mitigations
- **Figma MCP unavailable or values differ from spec** — spec defines fallback
  defaults (suffix hints, 1440px cap); build proceeds with those and visually
  verifies.
- **Google Fonts unreachable** — `system-ui` fallback in the font stack; page
  must render fully without the network font (tested with fonts blocked).
- **"activity" SVG renders incorrectly** — already exported locally to
  `frontend/assets/activity.svg`; verify visually, re-export if broken.
- **Footer links 404** — expected until F2 ships; noted in spec.
- **Regression in Predict flow during markup restructure** — AC9 check is a
  dedicated step (Step 11) run before the code PR; payload verified in
  Network tab against the pre-change baseline.

## 9. Open Questions
None.