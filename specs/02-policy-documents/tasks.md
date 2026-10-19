# Tasks 02 — Policy Documents

**Status:** Draft
**Feature ID:** F2
**Branch:** feat/02-policy-documents
**Plan:** specs/02-policy-documents/plan.md (Approved)
**Created:** 2026-10-18

Tasks map 1:1 to plan Section 5 steps. Mark `- [x]` when done and validated.

## Build

- [ ] T1. Create `frontend/privacy.html`: copy the landing-page shell verbatim
      (head with meta/fonts/`assets/styles.css`, `page-header` block, `page-footer`
      block with all three relative links); set per-page `<title>` and fill
      `<main>` with a Privacy Policy title + 3–5 heading/paragraph sections of
      clearly generic placeholder text. — plan Step 1 (AC1, AC4–AC8)
- [ ] T2. Create `frontend/terms.html`: same shell verbatim; placeholder
      Terms & Conditions sections. — plan Step 2 (AC2, AC4–AC8)
- [ ] T3. Create `frontend/about.html`: same shell verbatim; short placeholder
      About Us description. — plan Step 3 (AC3, AC4–AC8)
- [ ] T4. Review each page's `<main>` against the shared stylesheet in a browser;
      only if the plain-text layout needs support, append new additive classes
      at the bottom of `frontend/assets/styles.css` (no existing rule edited) and
      apply them to the three pages; otherwise leave the stylesheet untouched.
      Confirm the landing page is visually unaffected if CSS was added.
      — plan Step 4 (AC6, AC9)

## Validate (before code PR — Gate 2)

- [ ] T5. Local navigation pass: open all three pages via file system and via a
      local static server; from each page click Home / Privacy / Terms / About Us;
      brand image resolves; verify copied header/footer blocks diff cleanly against
      `frontend/index.html` (head lines ~1–11, header ~14–24, footer ~162–171).
      — plan Step 5 (AC4, AC5, AC10)
- [ ] T6. Responsive pass: device-emulate ~375px width on each page — no
      horizontal scrollbar, no overlapping text; typography matches the landing
      page. — plan Step 5 (AC9)
- [ ] T7. Content review: confirm all body copy is clearly generic placeholder
      (no page presents fabricated legal claims as the site's actual policies).
      — plan Step 6 (AC8)
- [ ] T8. Local HTML checking of the three new files (e.g., `html5validator`
      pointed at `frontend/`) before pushing. — plan Step 6 (AC11)

## Commit & PR (Gate 2)

- [ ] T9. Commit code (`feat: add placeholder privacy, terms, and about pages
      for F2`) and push. SDD step 10.
- [ ] T10. Open code-review PR against main; confirm CI html5validator job
      (root: `frontend/`) green on the PR; merge after review. SDD steps 11–12.
      — plan Step 7 (AC11)
- [ ] T11. Post-merge: after the GitHub Pages build, on the live landing page
      click Privacy, Terms & Conditions, and About Us — all three resolve; spot-
      check each page end-to-end. — plan Step 8 (AC1, AC2, AC3)
- [ ] T12. Post-deploy mobile pass (~375px emulation) on the live pages.
      — plan Step 9 (AC9)