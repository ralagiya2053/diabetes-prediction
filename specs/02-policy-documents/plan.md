# Plan 02 — Policy Documents

**Status:** Draft
**Feature ID:** F2
**Branch:** feat/02-policy-documents
**Spec:** specs/02-policy-documents/spec.md
**Author:** Rushikesh Alagiya
**Created:** 2026-10-18

## 1. Approach Summary
Create three static HTML pages under `frontend/` (privacy, terms, about) that copy the
landing page's `<head>` setup, Header, and Footer markup verbatim — brand asset, Google
Fonts links, and `assets/styles.css` all resolve identically because the pages live in
the same directory as `index.html`. The `<main>` of each page is a plain document
layout: page title plus heading/paragraph sections rendered with the existing shared
typography. If the existing stylesheet has no suitable classes for plain-text body
content, we append a small set of new, additive classes at the end of `styles.css`
(existing rules untouched). Placeholder legal/info copy is authored directly in the
HTML; no JS, no API calls, no build tooling.

## 2. Files to Create
- `frontend/privacy.html` — Privacy Policy page: landing-page header/footer + placeholder
  policy sections (AC1, AC4–AC8)
- `frontend/terms.html` — Terms & Conditions page: same shell + placeholder terms
  sections (AC2, AC4–AC8)
- `frontend/about.html` — About Us page: same shell + short project/team description
  (AC3, AC4–AC8)
- `specs/02-policy-documents/tasks.md` — written next, after this plan is merged (SDD
  step 7); not part of the code PR

## 3. Files to Modify
- `frontend/assets/styles.css` — **additive only, if needed**: new page-scoped classes at
  the bottom of the file for the document-body layout (e.g., content max-width, left-
  aligned section spacing). No existing rule is edited, moved, or deleted. If existing
  classes prove sufficient, this file is NOT modified at all.
- No frozen files (`app/`, `Dockerfile`, model artifacts, `train/diabetes.csv`) are
  touched. `frontend/index.html` is not modified — its footer links become live
  automatically once the new pages deploy.

## 4. Architecture / Data Flow
Pure static-site addition; no runtime data flow.

```
GitHub Pages (served from repo root)
├── frontend/index.html        (existing — unchanged)
├── frontend/privacy.html      (new)
├── frontend/terms.html        (new)
├── frontend/about.html        (new)
└── frontend/assets/styles.css (shared by all four; unchanged or additive-only)

Page structure of each new file:
  <head>  — same meta/font/stylesheet links as index.html, per-page <title>
  <header class="page-header"> ... </header>   ← copied verbatim
  <main>    — <h1> page title, <h2>/<p> placeholder sections
  <footer class="page-footer"> ... </footer>   ← copied verbatim
```

Navigation is ordinary `<a href="...">` between the four pages; relative paths only, so
each page also works when opened directly from disk for local review.

## 5. Step-by-Step Implementation
1. Copy the full head/header/footer shell of `frontend/index.html` into a new
   `frontend/privacy.html`; set `<title>` and `<main>` to placeholder Privacy Policy
   sections (title + 3–5 heading/paragraph sections of clearly generic dummy text).
   — satisfies AC1, AC4, AC5, AC6, AC7, AC8
2. Repeat for `frontend/terms.html` with placeholder Terms & Conditions sections.
   — satisfies AC2, AC4, AC5, AC6, AC7, AC8
3. Repeat for `frontend/about.html` with a short placeholder About Us description.
   — satisfies AC3, AC4, AC5, AC6, AC7, AC8
4. Review each page's `<main>` in a browser against the shared stylesheet. Only for
   layout gaps, append new additive classes to the bottom of `frontend/assets/styles.css`
   and apply them to the three pages' `<main>` content. Keep existing rules untouched.
   — satisfies AC6, AC9
5. Manual pre-PR validation: open all three pages locally, click through every
   header/footer link, verify brand image resolves, and resize to ~375px width.
   — satisfies AC4, AC6, AC9, AC10
6. Run local HTML checking (e.g., `html5validator` or an HTML5 validator against the
   three new files) before pushing, then commit `feat:`+push the branch.
   — satisfies AC11
7. Open PR to `main` (Gate 2: Code Review), merge, confirm CI's html5validator job
   (root: `frontend/`) passes on the PR and after merge.
   — satisfies AC11
8. Post-merge, GitHub Pages redeploys; click each of the three footer links on the live
   landing page and confirm they now resolve.
   — satisfies AC1, AC2, AC3
9. Optional post-deploy pass at ~375px width on the live pages (mobile emulation).
   — satisfies AC9

Suggested commit messages (SDD steps noted):
- Steps 1–3: `feat: add placeholder privacy, terms, and about pages for F2 (Gate 1 spec merged, SDD steps 5-6)`
- Step 4 (if needed): `feat: add page-scoped document layout styles for F2 policy pages`
- Step 6: `feat: F2 policy pages validated against approved spec before PR (Gate 2, SDD step 9)`

## 6. Test Strategy
- Manual (local, before PR — step 5):
  - Open each page via the file system and via a local static server; check layout and
    brand image in both cases (catches absolute-path mistakes).
  - From each page, click Home, Privacy, Terms, About Us — all four navigate correctly
    (AC4, AC5, AC10).
  - Narrow the window / device-emulate 375px: no horizontal scrollbar, no overlap (AC9).
- Automated:
  - Existing CI (`html5validator` over `frontend/`) validates all three new files on the
    PR and post-merge (AC11).
  - No pytest additions — this feature has no Python surface; `tests/` remains untouched.
- AC verification map:
  - AC1–AC3 → manual clicks on deployed site after merge (step 8)
  - AC4–AC7 → manual review of each page (steps 1–3, 5)
  - AC8 → content review during PR code review (placeholder dummy text only)
  - AC9 → manual mobile-width check (steps 5, 9)
  - AC10 → manual browser Back-button check (step 5)
  - AC11 → local HTML check (step 6) + CI job green (step 7)

## 7. Rollout & Rollback
- **Deploy:** merge to `main`; GitHub Pages serves the site with the new pages on the
  next Pages build (no Lambda/infra involvement — purely static files).
- **Rollback:** `git revert` the merge commit and push `main`; CI/Pages then redeploy
  with only the header/footer links 404ing again (the pre-F2 state, known-good).
- No database, no model, no backend state — rollback risk is nil.

## 8. Risks & Mitigations
- **Existing styles.css lacks text-document layout classes** → plan allows appending new
  additive classes only; any added rules are scoped to new class names so the landing
  page is visually unaffected (verified by reviewing the landing page after the CSS
  change).
- **Drift between a copied header/footer and `index.html`** → markup is copied verbatim
  in the same directory (identical relative paths); a manual diff of the copied blocks
  against `index.html` lines 1–24 and 162–171 can be done during review.
- **Placeholder text read as real policy** → content authored with clearly generic dummy
  wording and a visible note that final policy text is pending; AC8 enforces during
  review.
- **CI validation rejects something in the new pages (e.g., stray markup)** → run local
  HTML checking before pushing (step 6) so CI is not the first feedback loop.

## 9. Open Questions
None.