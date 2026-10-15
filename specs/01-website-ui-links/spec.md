# Spec 01 — Website UI: nav + footer links

**Status:** Draft
**Feature ID:** F1
**Branch:** feat/01-website-ui-links
**Author:** Rushikesh Alagiya
**Created:** 2026-10-15

## 1. Problem Statement
The current frontend lacks a consistent global navigation and footer, making the application feel incomplete and providing no easy way for users to access policy documents or about information. This feature adds a standardized header and footer across the site to improve professional appearance and navigation.

## 2. Scope
**In scope:**
- Implementation of a global Page Header featuring the product identity (icon and name) and page category.
- Implementation of a global Page Footer featuring the product name and navigation links (Privacy, Terms & Conditions, About Us).
- Responsive layout for header and footer.
- Integration of the "activity" health icon.

**Out of scope:**
- Implementation of the actual destination pages for "Privacy", "Terms & Conditions", and "About Us" (covered in F2).
- Complex navigation menus or dropdowns.
- Changes to the main assessment form logic.

## 3. User-Facing Behavior
Users will now see a consistent header at the top of every page containing the "Diabetes Risk Predictor" branding and a footer at the bottom of the page. The footer provides clear, clickable links to the site's legal and informational pages.

## 4. Acceptance Criteria
1. The header must match the Figma design (Node 3:30) with a height of 88px, 64px horizontal padding, and the "activity" icon rendered as a 22x22px SVG.
2. The footer must match the Figma design (Node 3:112) with a height of 92px, 64px horizontal padding, and links rendered in `#1e3a8a` blue.
3. The header and footer must be present on the main index page.
4. Footer links must use href="/privacy.html", /terms.html, /about.html and open in the same window.
5. The layout must be centered on screen widths of 1440px, with content contained within the design's specified margins.

## 5. Non-Goals
- Creating a full-scale design system for the entire site.
- Implementing server-side rendering for the static frontend.

## 6. Dependencies
- Figma design file for visual reference.
- Static HTML/CSS frontend in `frontend/index.html`.
- F2 (Policy documents) depends on this for the link placements.

## 7. Risks & Unknowns
- Ensure the "activity" SVG is exported and hosted locally to avoid temporary Figma URL expiration.
- Footer links will return 404 errors until Feature F2 (Policy documents) is implemented and the corresponding HTML files are created.

## 8. Open Questions
None.

## 9. References
- Figma Design: [Diabetes Risk Predictor](https://www.figma.com/design/3SLCGqAA6eKHHLNkymEnEz/Untitled?node-id=0-1)
