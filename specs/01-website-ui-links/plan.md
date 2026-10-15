# Plan 01 — Website UI: nav + footer links

**Status:** Draft
**Feature ID:** F1
**Branch:** feat/01-website-ui-links
**Author:** Rushikesh Alagiya
**Created:** 2026-10-15

## 1. Approach
The goal is to implement a global header and footer as per Figma design (Nodes 3:30 and 3:112). Since the current frontend is a single static HTML file (`frontend/index.html`), I will update the file to include these new sections and their corresponding styles.

### Visual Implementation
- **Header**: Inserted at the top of the `<body>`. It will use a flexbox layout to separate branding (left) from the category label (right).
- **Footer**: Inserted at the bottom of the `<body>`. It will use a flexbox layout to separate branding (left) from navigation links (right).
- **Styling**: I will update the `<style>` block of `index.html` to accommodate full-width components. I will use absolute measurements for heights and padding as specified in the ACs.

### Asset Management
- The "activity" SVG will be acquired via the Figma MCP `get_design_context` tool or exported manually and saved to `frontend/assets/activity.svg`.
- The SVG must be constrained to render at exactly 22x22px.

## 2. Technical Changes
- **File: `frontend/index.html`**
    - Add `<header>` section at the top of `<body>`.
    - Add `<footer>` section at the bottom of `<body>`.
    - Update CSS in `<style>` block:
        - Reset `body` margin/padding to 0.
        - Introduce a `.container` wrapper for existing form content to center it with design margins.
        - Add specific CSS for `.page-header` (88px height, white bg, bottom border) and `.page-footer` (92px height, top border).
        - Apply `#1e3a8a` color to footer links.

- **New Directory: `frontend/assets/`**
    - Create directory to hold `activity.svg`.

## 3. Verification Plan
- **Visual Match**: Compare the rendered page against Figma screenshots.
- **Measurement Check**: Inspect elements to verify:
    - Header height = 88px.
    - Footer height = 92px.
    - Horizontal padding = 64px.
    - Icon size = 22x22px.
- **Link Validation**: Verify "Privacy", "Terms & Conditions", and "About Us" links point to `/privacy.html`, `/terms.html`, and `/about.html` and open in the same window.
- **Layout Stability**: Verify the page does not exhibit horizontal scrolling across viewports from 1024px to 1920px.

## 4. Architecture / Data Flow
`User Browser` $\rightarrow$ `GitHub Pages (Static Hosting)` $\rightarrow$ `frontend/index.html`
- Header/Footer: Static HTML/CSS.
- Assets: Local file reference (`/assets/activity.svg`).
- Links: Relative paths to static HTML files in the same directory.

## 5. Step-by-Step Implementation
1. **Asset Acquisition**: Extract "activity" SVG and save to `frontend/assets/activity.svg`. (Satisfies AC1)
2. **Global Styles**: Reset `body` margins and implement the `.container` class to center content and prevent horizontal scroll from 1024px-1920px. (Satisfies AC5)
3. **Header Implementation**: Add `<header>` with branding and category label using Figma Node 3:30 specs. (Satisfies AC1, AC3)
4. **Footer Implementation**: Add `<footer>` with branding and links using Figma Node 3:112 specs. (Satisfies AC2, AC3)
5. **Link Wiring**: Set `href` for footer links to `/privacy.html`, `/terms.html`, and `/about.html` ensuring they open in the same window. (Satisfies AC4)
6. **Final Styling**: Apply exact colors, height, and padding as per design. (Satisfies AC1, AC2)

## 6. Test Strategy
### Manual Testing
- **Visual Audit**: Side-by-side comparison with Figma screenshots for Header and Footer.
- **Link Testing**: Click each footer link and verify the browser attempts to load the correct URL in the current tab.
- **Viewport Testing**: Resize browser window between 1024px and 1920px to confirm no horizontal scrollbars appear.

### Automated Testing
- **HTML Validation**: Run `frontend/index.html` through a W3C validator to ensure no syntax errors.
- **Link Integrity**: Use a basic shell script or tool to check for `href` presence of the three target policy files.

## 7. Rollout & Rollback
- **Rollout**: Merge `feat/01-website-ui-links` $\rightarrow$ `main`. GitHub Pages automatically deploys the updated `frontend/index.html`.
- **Rollback**: Perform `git revert` on the merge commit to `main`. GitHub Pages will rebuild and restore the previous version of the frontend.

## 8. Risks & Mitigations
- **Risk**: Figma temporary asset URLs expire.
- **Mitigation**: Download and host the "activity" SVG locally in `frontend/assets/` before committing code.
- **Risk**: Broken links.
- **Mitigation**: Accept 404s as expected behavior until Feature F2 is merged.

## 9. Open Questions
None.