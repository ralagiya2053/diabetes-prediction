# Spec 02 — Policy Documents

**Status:** Approved
**Feature ID:** F2
**Branch:** feat/02-policy-documents
**Author:** Rushikesh Alagiya
**Created:** 2026-10-18

## 1. Problem Statement
The F1 landing page footer links to Privacy, Terms & Conditions, and About Us, but none
of those pages exist — every footer link currently 404s. A portfolio site whose legal/info
links are broken undermines credibility, and a health-data tool with no way to state how
user inputs are handled looks incomplete. F2 fixes this by standing up the three missing
pages as part of the site.

## 2. Scope
**In scope:**
- Three new static pages: Privacy Policy, Terms & Conditions, and About Us.
- Each page reuses the exact same Header and Footer markup as the landing page, with
  relative links between the four pages (landing ↔ privacy, terms, about).
- Each page links to the existing shared stylesheet so header, footer, and typography
  styling stay consistent with the landing page.
- Main body content is clean, readable text in a standard legal/info layout.
- Body copy uses clearly-labeled placeholder dummy text (real policy wording comes later).

**Out of scope:**
- Any changes to the landing page (`frontend/index.html`) — its footer already links to
  the three pages, so it needs no edits.
- Drafting real legal text (privacy notices, terms clauses, medical disclaimers).
- `charges.html` and `compliance.html` — dropped.
- Anything related to the RAG chatbot (separate future feature, F3/F4).

## 3. User-Facing Behavior
**Before:** From the landing page footer, clicking Privacy, Terms & Conditions, or About
Us returns a 404.

**After:** Each footer link opens its own page that looks like part of the same site:
- A visitor landing on the Privacy page (or Terms, or About) sees the same site header —
  brand mark, name, "Health assessment" label — as the landing page, and the same footer.
- Below the header is a page title and well-spaced readable text sections (headings and
  paragraphs) appropriate to the page: privacy policy text on Privacy, terms text on
  Terms & Conditions, and a short team/project description on About Us.
- The header brand and footer links navigate back between all four pages, so the site
  feels connected rather than a one-page app plus dead links.
- Pages are readable on desktop and mobile widths, consistent with the landing page.

The legal text itself is placeholder copy; visitors see clearly generic dummy text, and
the pages are structurally ready for real wording to replace it later.

## 4. Acceptance Criteria
1. From the deployed site, clicking **Privacy** in the footer opens a Privacy Policy page
   (no 404).
2. Clicking **Terms & Conditions** in the footer opens the Terms page (no 404).
3. Clicking **About Us** in the footer opens the About Us page (no 404).
4. Each new page's Header section is identical to the landing page's header, with the
   brand image resolving correctly (relative asset path, no broken image).
5. Each new page's Footer section is identical to the landing page's footer, and all
   three footer links work from every new page (returning to the landing page and to the
   other two pages).
6. Each new page loads the existing shared stylesheet, and its header, footer, and body
   typography (font family, colors, spacing) visually match the landing page.
7. Each page shows readable body content — a page title plus heading-and-paragraph
   sections in a standard legal/info layout.
8. The body text is placeholder dummy text; no page presents fabricated legal claims as
   the site's actual policies.
9. Each page renders correctly at mobile width (e.g., 375px) with no horizontal
   scrollbar or overlapping text.
10. Clicking the browser Back button from any new page returns to where the visitor came
    from (pages use standard client-side navigation only).
11. The HTML of each page passes the project's existing CI HTML validation (same
    validation applied to `frontend/index.html` in the F1 CI workflow).

## 5. Non-Goals
- Real or legally-reviewed policy text.
- Cookie consent banner or any consent mechanism.
- Medical disclaimer changes — the existing on-page disclaimer on the landing page stays
  as is (it lives in the frozen `app`/"existing prediction service" scope only to the
  extent F2 must not alter it).
- New CSS files or design-system changes — pages reuse the existing stylesheet.
- Routing, JS interactivity, or API calls on the new pages (static text only).
- Contact forms, newsletter signups, or any data collection UI.

## 6. Dependencies
- **F1 (complete):** the landing page redesign already provides the exact Header and
  Footer markup, the shared stylesheet, and the footer links these pages fulfil.
- **Static hosting (GitHub Pages):** pages deploy the same way as `frontend/index.html`.
- **Files this feature will touch:** new files only — three HTML pages under `frontend/`.
  No modification to `frontend/index.html`, `frontend/assets/`, `app/`, `Dockerfile`,
  model artifacts, or `train/diabetes.csv` (frozen / additive-only per CLAUDE.md).

## 7. Risks & Unknowns
- Placeholder text is not legal text: the Privacy page in particular does not currently
  make accurate statements about how the app transmits health inputs to the API. The
  site should not be presented as production-ready until real policy wording replaces
  the dummies (see Non-Goals).
- The shared stylesheet's layout classes (e.g., `page-shell`, two-column form grids) are
  built around the landing page; the body layout for the new pages may need a small
  amount of page-scoped styling if existing classes don't suit plain text. Spec leaves
  the approach to the plan, with the constraint that no existing styles change.
- GitHub Pages deploy timing means acceptance criteria 1–3 verify against the deployed
  site only after merge.

## 8. Open Questions
None.

## 9. References
- Landing page (live): https://ralagiya2053.github.io/diabetes-prediction/frontend/index.html
- F1 spec: `specs/01-website-ui-links/spec.md`
- Broken footer links in `frontend/index.html:166-168`