# Tasks 01 — Website UI: Full page redesign to match Figma

**Status:** Draft
**Feature ID:** F1
**Branch:** feat/01-website-ui-links
**Plan:** specs/01-website-ui-links/plan.md (Approved)
**Created:** 2026-10-18

Tasks map 1:1 to plan Section 5 steps. Mark `- [x]` when done and validated.

## Build

- [ ] T1. Attempt Figma MCP design-context pull (Nodes 3:30, 3:112, page frame):
      hint placement, card max-width, colors. Record outcome; fall back to spec
      defaults (suffix hints, 1440px cap) if unavailable. — plan Step 1 (AC3, AC5)
- [ ] T2. Base styles in `frontend/assets/styles.css`: reset, CSS tokens
      (off-white `#f7f8fa`, dark blue `#1e3a8a`, spacing), 1440px centered
      content cap, Inter via Google Fonts with preconnect hints + `system-ui`
      fallback. — plan Step 2 (AC10)
- [ ] T3. Header markup + styles: 88px height, 64px padding, 38×38 blue tile
      with 22×22 `activity.svg`, product name left, "Health assessment" right;
      <768px: 24px padding, label hidden. — plan Step 3 (AC1)
- [ ] T4. Hero section: eyebrow / centered title / subtitle, spec copy
      verbatim. — plan Step 4 (AC2)
- [ ] T5. Form card shell: white rounded card, border/shadow, "Your health
      details" heading, subtext, "8 health indicators" badge top-right with
      icon. — plan Step 5 (AC3)
- [ ] T6. Form grid: two columns ≥1024px, single column below; pairs
      Gender+Age, Hypertension+Heart disease, Smoking history+BMI,
      HbA1c+Blood glucose. — plan Step 6 (AC4)
- [ ] T7. Field hints: years, "0 = No · 1 = Yes" (×2), kg/m², %, mg/dL;
      placement per T1 outcome. — plan Step 7 (AC5)
- [ ] T8. Card footer row: "Ready when you are" + subtext left; Predict button
      right (dark blue, white text, arrow icon). — plan Step 8 (AC6)
- [ ] T9. Disclaimer below card: centered, info icon, spec text verbatim.
      — plan Step 9 (AC7)
- [ ] T10. Page footer: 92px height, 64px padding, branding left, nav links
      right in `#1e3a8a`, relative hrefs `privacy.html` / `terms.html` /
      `about.html`, same window; <768px: 24px padding. — plan Step 10 (AC8)
- [ ] T11. Restyle result/error block to card design; verify Lambda payload
      and displayed content unchanged. — plan Step 11 (AC9)

## Validate (before code PR — Gate 2)

- [ ] T12. Responsive + stability pass: no horizontal scroll ≥1024px; 1440px
      cap centered; single column + 24px padding <768px. — plan Step 12 (AC4, AC10)
- [ ] T13. Manual per-AC checklist (plan Section 6): measurements, verbatim
      copy, payload comparison in Network tab, error path, Google Fonts
      blocked-mode fallback, footer link behavior (404 expected until F2).
- [ ] T14. CI green (HTML validation).

## Commit & PR (Gate 2)

- [ ] T15. Commit code (`feat: rebuild landing page per Figma redesign (F1)`)
      and push. SDD steps 10.
- [ ] T16. Open code-review PR against main; merge after review. SDD steps 11–12.