# Plan 04 — Chatbot Widget

**Status:** Draft
**Feature ID:** F4
**Branch:** feat/04-chatbot-widget
**Spec:** specs/04-chatbot-widget/spec.md
**Author:** Rushikesh Alagiya
**Created:** 2026-10-19

## 1. Approach Summary

The widget is a self-contained vanilla-JS module whose DOM (FAB + chat panel)
is injected into each page by a single script tag — GitHub Pages has no
server-side includes, so a one-line script include per page keeps the HTML
change minimal and avoids copy-pasting markup four times. All widget styles
are appended to the existing stylesheet and consume the F1 design tokens
(`--color-*`, `--radius-*`) already defined there, so no new framework or
token set is introduced. Chat exchanges talk to the deployed F3 `/ask`
endpoint with `fetch` + `AbortController` (~30s timeout for Lambda +
cold-start + Bedrock latency), and every backend surface (loading, error,
sources, insufficient-context answer) maps to an explicit UI state.

## 2. Files to Create

- `frontend/chatbot/chat.js` — the entire widget: FAB + panel markup
  injection, open/close handling, message rendering, fetch + timeout, client
  validation, error/loading/sources states. One `API_URL` constant at the top
  is the single place the Function URL is configured.
- `frontend/assets/chat.svg` — chat-bubble icon for the FAB (matches the
  flat single-icon SVG pattern of `activity.svg`, `info.svg`, etc.).

Dependencies: none new (no npm/pip/CDN packages; vanilla JS + CSS only).

## 3. Files to Modify

- `frontend/assets/styles.css` — append a clearly-commented `/* F4 — Chatbot
  widget */` section using the existing tokens; no existing rules changed, so
  F1/F2 layout is untouched.
- `frontend/index.html`, `frontend/privacy.html`, `frontend/terms.html`,
  `frontend/about.html` — add one line before `</body>`:
  `<script src="chatbot/chat.js" defer></script>` (plus the widget's
  root element is injected by the script, so no markup duplication). Also add
  `<link rel="icon" href="assets/chat.svg">` only if needed — default: no.

Frozen files (`app/`, `rag-backend/`, `Dockerfile*`, `train/`): **not
touched** — the widget consumes the backend over HTTP only.

## 4. Architecture / Data Flow

```
Browser (GitHub Pages, all 4 pages)
  └─ <script src="chatbot/chat.js" defer>
       └─ injects: #chat-fab button + #chat-panel (dialog, messages, input, send)
            │  user types question → trim/length validation (client-side)
            │  render user bubble → render "Thinking…" indicator
            ▼
     fetch(POST API_URL + "/ask")          ← Function URL, CORS from F3 middleware
       {"question": "<1..1000 chars>"}
            │  AbortController timeout ≈ 30s → friendly retry error
            ▼
        200 {"answer", "sources"} → answer bubble + source chips
        422/4xx  {"detail"}       → show detail in an error bubble
        5xx / network / timeout   → friendly error bubble; input re-enabled
```

State kept in-page only: open/closed flag, message list (also serves as
history while the page lives). No localStorage, no persistence, no streaming.

## 5. Step-by-Step Implementation

1. **Add `frontend/assets/chat.svg`** (bubble outline using the F1 accent
   color family) — prerequisite for the FAB.
2. **Create `frontend/chatbot/chat.js`: markup injection.** Module defines
   the widget DOM once and injects it into `document.body` on load
   (`defer`). FAB is a `<button>` with `aria-label="Open chat"` +
   `aria-expanded`; panel is a `role="dialog"`/`aria-label="Assistant chat"`
   containing header (title + close `<button aria-label="Close chat">`),
   scrollable `#chat-messages` log (`role="log"`, `aria-live="polite"`),
   input (`<label>`-associated) and send `<button>`. — covers AC1, AC2
   (markup half), AC3 (welcome message logged on first open).
3. **Append widget CSS to `styles.css`.** Section consumes
   `var(--color-accent)`, `--radius-card`, `--shadow-card`, Inter stack,
   etc. Fixed-position FAB bottom-right; panel card above it
   (~360×480 desktop); `max-width: calc(100vw - 32px)` + capped height and
   internal scroll at small viewports; `prefers-reduced-motion` respected.
   No existing rule is edited. — covers AC1 (non-overlapping placement),
   AC12 (design tokens), AC11 (sizing half).
4. **Wire open/close + focus/keyboard.** Toggle `hidden`/class; Enter/Space
   work natively on `<button>`; Escape closes; basic focus handling (panel
   focuses the input on open, focus returns to FAB on close). — covers AC2.
5. **Implement send flow + validation.** Submit on send button and on Enter
   in the input; trim; empty → reject locally (no request, brief shake or
   hint); > 1000 chars → block locally with an inline warning. User bubble
   appended; input cleared/disabled; "Thinking…" indicator appended. —
   covers AC4 (client half), AC8, AC9.
6. **Implement fetch + render.** `POST {API_URL}/ask` with `AbortController`
   (~30s). Render: 200 → answer bubble (`textContent` only — no innerHTML
   for backend text; sources from `sources` as small chips/caption, omitted
   when empty so the insufficient-context answer renders bare); 4xx/422 →
   readable error bubble from `detail`; 5xx/network/timeout → friendly
   "The assistant is unavailable right now — please try again." error
   bubble; in every case the indicator is replaced and the input re-enabled
   so the next attempt works immediately. — covers AC4 (response half),
   AC5, AC6, AC7, AC10 (client half).
7. **Include the script on all four pages** — one `<script defer>` line per
   HTML file. — covers AC1 (all pages).
8. **Validate against the live site** (see Section 6) and run the frozen-
   file check. Commit each numbered batch with conventional messages
   (`feat: …` for 2–7, `chore:` or `feat:` for assets), referencing this plan.
   — covers AC13.

## 6. Test Strategy

**Automated:** none added. The repo's pytest suite can't exercise JS, and a
JS unit-test runner (node/vitest) would be a new dependency the spec excludes.
Backend behavior is already covered by `tests/test_ask.py` (F3).

**Manual validation checklist — each AC to a check:**

| AC | Check |
|----|-------|
| 1 | Open each of the 4 live pages; FAB visible bottom-right, above footer, nothing obscured. |
| 2 | Click FAB open/close; keyboard Tab to FAB, Enter/Space open; Escape and close button close. |
| 3 | Fresh open shows welcome message. |
| 4 | Send "What is your privacy policy?": user bubble → Thinking… → answer; timing feels intentional. |
| 5 | Answer shows source chips matching the returned `sources`. |
| 6 | Send an off-topic question (e.g. "Tell me about sports"): no chips, insufficiency answer text renders, no error. |
| 7 | Block network in DevTools (or curl the URL with an empty index): error bubble appears, input re-enabled, retry succeeds. |
| 8 | Send whitespace-only: no request in the Network tab. |
| 9 | Paste >1000 chars: blocked locally with warning, no request. |
| 10 | From the live GitHub Pages origin, a real Q&A roundtrip succeeds (check Network tab: 200, correct CORS headers, no duplicate `Access-Control-Allow-Origin`). |
| 11 | Test at ≤400px viewport and desktop (no horizontal scroll, no content pushed). |
| 12 | Compare FAB/panel colors/radii/fonts against F1 tokens and Figma (visual pass). |
| 13 | `git diff main…HEAD --name-only` shows no changes under `app/`, `rag-backend/`, `Dockerfile`, `train/`. |

Also verify via curl against the live endpoint before wiring:
`curl -X POST <URL>/ask -H "Content-Type: application/json" -d '{"question":"What is your privacy policy?"}'`
to confirm the expected response shape the widget must render.

## 7. Rollout & Rollback

**Deploy:** merge the PR — GitHub Pages automatically serves the updated
`frontend/` from `main`. No AWS changes, no Lambda redeploy, no new IAM.

**Rollback:** a single `git revert` of the chatbot merge removes the script
tags and files; the widget degrades to nothing (no FAB) rather than breaking
pages. If only the widget misbehaves with correct rollback timing, set
`API_URL`'s module-level flag so the script no-ops until fixed (a one-line
revert to `chat.js` alone redeploys on next Pages build). All backend state
is untouched by any rollback.

## 8. Risks & Mitigations

- **Cold start + Bedrock latency (several seconds, occasionally >10s)** —
  generous ~30s timeout, persistent "Thinking…" indicator with subtle elapsed
  hint if needed; welcome message sets expectations about what the assistant
  knows.
- **XSS via backend text injected as HTML** — all backend-provided text
  (answers, sources, error details) is inserted with `textContent` /
  `createElement` only; no `innerHTML` with remote content.
- **Silent breakage if the Function URL changes** — `API_URL` lives in
  exactly one place at the top of `chat.js`; errors surface visibly in the
  UI rather than silently failing.
- **Duplicate CORS headers / live-origin mismatch** — F3 doc states Function
  URL CORS is disabled and the app middleware handles it; AC10 checklist
  validates from the live origin, never only localhost.
- **Panel pushing page layout on small screens** — widget uses
  `position: fixed` and its own scroll context, so page flow is never
  affected; explicit `max-height` / `max-width` rules for small viewports.
- **Multi-turn confusion** — out of scope by spec; the insufficiency answer
  renders gracefully (AC6), and the welcome message explains the assistant's
  scope.

## 9. Open Questions

None. Endpoint URL, pages, sources display, loading/error states, and the
no-framework constraint are all settled in the spec and the user's scope
statement.