# Spec 01 — Website UI: Full page redesign to match Figma

**Status:** Approved
**Feature ID:** F1
**Branch:** feat/01-website-ui-links
**Author:** Rushikesh Alagiya
**Created:** 2026-10-15

## 1. Problem Statement
The current frontend is a bare HTML form with no visual hierarchy, no branding, and no
trust signals. It looks like a prototype, not a product. This feature rebuilds the
landing page to match the Figma design — adding a hero section, a card-based form
layout, inline field hints, a branded header and footer, and a disclaimer — while
keeping the existing ML prediction endpoint intact.

## 2. Scope

**In scope:**
- Page header: activity icon, "Diabetes Risk Predictor" branding, "Health assessment" label
- Hero section: eyebrow text ("A LITTLE INSIGHT. A FIRST STEP."), large title, subtitle
- Form card: white rounded card containing the existing input fields, with a
  "Your health details" heading and an "8 health indicators" badge
- Two-column grid layout for form inputs (desktop), single column (mobile)
- Inline hints on fields (years, kg/m², %, mg/dL, "0 = No · 1 = Yes")
- Custom Predict button (dark blue, arrow icon, right-aligned within card)
- Disclaimer line below the card with an info icon
- Page footer: branding on left, nav links (Privacy, Terms & Conditions, About Us) on right
- Off-white page background
- Wire Predict button to the existing Lambda endpoint (no API changes)

**Out of scope:**
- Implementation of destination pages for Privacy, Terms & Conditions, About Us (F2)
- RAG chatbot / widget (F3, F4)
- Changes to the ML model, Lambda function, or API contract
- Mobile-first redesign beyond responsive stacking
- Dark mode, theming, or a design system

## 3. User-Facing Behavior

**Before:** Plain HTML form on white background. Small heading, no branding, no context.
Fields stacked vertically with labels. Default gray Predict button.

**After:** Branded page with a header and footer. A clear hero section tells the user
what this tool is and what to do. The form sits inside a clean white card with a
two-column layout. Each field has an inline unit hint. A dark blue Predict button
anchors the card. A disclaimer reminds the user this is informational, not medical
advice. Visual hierarchy guides the eye from eyebrow → title → card → disclaimer.

## 4. Acceptance Criteria

1. **Header** matches Figma Node 3:30 — height 88px, 64px horizontal padding,
   activity icon 22×22 SVG inside a 38×38 rounded blue tile, product name left,
   "Health assessment" label right. At <768px, horizontal padding drops to 24px
   and the "Health assessment" label is hidden; height stays 88px.
2. **Hero section** matches Figma — eyebrow line "A LITTLE INSIGHT. A FIRST STEP."
   (uppercase, letter-spaced, small), large centered title "Diabetes Risk Predictor",
   subtitle "Enter your health details below to explore your estimated diabetes risk."
3. **Form card** — white background, rounded corners, subtle border/shadow,
   max-width matches Figma, contains heading "Your health details", subtext
   "Review each value before making a prediction.", and a badge reading
   "8 health indicators" with an icon, positioned top-right.
4. **Form layout** — two-column grid on desktop (≥1024px), single column below
   1024px (which covers the <768px mobile breakpoint).
   Fields pair as: Gender+Age, Hypertension+Heart disease, Smoking history+BMI,
   HbA1c level+Blood glucose level.
5. **Field hints** — each input shows its unit or range inline. Hint placement
   follows the Figma design (pull via Figma MCP); if MCP is unavailable, default
   to a right-aligned suffix rendered inside the input field:
   - Age: "years"
   - Hypertension, Heart disease: "0 = No · 1 = Yes"
   - BMI: "kg/m²"
   - HbA1c level: "%"
   - Blood glucose level: "mg/dL"
6. **Predict button** — dark blue background, white text, arrow icon on the right,
   right-aligned within the card footer row (not the page footer). Card footer row
   reads "Ready when you are" with subtext "Use your current health measurements."
7. **Disclaimer** — below the card, centered, with an info icon. Text:
   "This estimate is for informational purposes only, not a medical diagnosis.
   Discuss any concerns about your health with a qualified healthcare professional."
8. **Footer** matches Figma Node 3:112 — height 92px, 64px padding, branding left,
   nav links right, link color #1e3a8a. Links use relative hrefs "privacy.html",
   "terms.html", "about.html", same window. At <768px, padding drops to 24px;
   height stays 92px.
9. **Predict functionality unchanged** — clicking Predict sends the same payload to
   the existing Lambda URL. The result/error block is restyled to match the new
   card design; its content (prediction, probability, error text) is unchanged.
10. **Layout stability** — no horizontal scroll at any viewport ≥1024px. Content
    max-width caps at 1440px, centered. Page background is off-white (#f7f8fa or
    Figma-equivalent), card and header/footer are white.

## 5. Non-Goals
- Building a design system or component library
- Adding new form fields or changing field validation
- Changing the ML model, Lambda, or API contract
- Animations or transitions beyond hover states
- Accessibility audit beyond semantic HTML

## 6. Dependencies
- Figma design file (Nodes 3:30, 3:112, and full page frame)
- Static HTML/CSS in `frontend/index.html`
- Existing Lambda endpoint (frozen — do not modify)
- F2 depends on the footer link placement introduced here

## 7. Risks & Unknowns
- "activity" SVG path data from Figma may render incorrectly; verify visually and
  re-export if broken.
- Inter font: decision made — loaded via Google Fonts with a `system-ui` fallback.
  If Google Fonts is unreachable, the page must still render correctly with the
  fallback.
- Pixel-perfect match to Figma is aspirational, not required. Match structure,
  hierarchy, colors, and spacing closely — exact pixel values only where specified
  in ACs.
- Footer links 404 until F2 ships.

## 8. Open Questions
None.

## 9. References
- Figma Design: [Diabetes Risk Predictor](https://www.figma.com/design/3SLCGqAA6eKHHLNkymEnEz/Untitled?node-id=0-1)
- Existing Lambda endpoint: https://xa22mu3snncho7eo5rxrua6qvm0ckdwu.lambda-url.us-east-1.on.aws/predict