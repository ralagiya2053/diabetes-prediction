# Tasks 04 — Chatbot Widget

**Status:** Draft
**Feature ID:** F4
**Branch:** feat/04-chatbot-widget
**Plan:** specs/04-chatbot-widget/plan.md (Approved)
**Created:** 2026-10-19

Tasks map 1:1 to plan Section 5 steps. Mark `- [x]` when done and validated.

## Build

- [x] T1. Add `frontend/assets/chat.svg` (chat-bubble icon matching the flat
      single-icon SVG pattern of `activity.svg`/`info.svg`) in the F1 accent
      color family. — plan Step 1 (prerequisite for AC1's FAB)
- [x] T2. Create `frontend/chatbot/chat.js`: inject FAB
      (`<button aria-label="Open chat" aria-expanded>` + `chat.svg`) and panel
      (`role="dialog"`, header + close button, scrollable
      `role="log" aria-live="polite"` messages area, label-associated text
      input, send button) into `document.body` on load; log the welcome
      message on first open; `API_URL` constant at the top of the module as
      the single place the Function URL is configured. — plan Step 2
      (AC1, AC2-markup, AC3)
- [x] T3. Append a commented `/* F4 — Chatbot widget */` section to
      `frontend/assets/styles.css` consuming existing tokens
      (`--color-accent`, `--radius-card`, `--shadow-card`, Inter): fixed FAB
      bottom-right above footer, ~360×480 desktop card panel,
      `max-width: calc(100vw - 32px)` + capped height with internal scroll at
      small viewports, `prefers-reduced-motion` respected; no existing rule
      edited. — plan Step 3 (AC1, AC11-sizing, AC12)
- [x] T4. Wire open/close in `chat.js`: toggle FAB/panel, Escape closes,
      close button works, input focused on open, focus returns to FAB on
      close, `aria-expanded` kept in sync. — plan Step 4 (AC2)
- [x] T5. Implement send flow: submit on send button and Enter in the input;
      trim; whitespace-only → rejected locally (no request); >1000 chars →
      blocked locally with inline warning; user bubble appended, input
      cleared/disabled, "Thinking…" indicator appended. — plan Step 5
      (AC4-client, AC8, AC9)
- [x] T6. Implement fetch + render in `chat.js`: `POST {API_URL}/ask` with
      `AbortController` (~30s); 200 → answer bubble via `textContent` only
      (no innerHTML with remote text) + source chips omitted when
      `sources` empty (insufficient-context path); 4xx/422 → readable error
      bubble from `detail`; 5xx/network/timeout → friendly retry error
      bubble; indicator replaced and input re-enabled on every outcome.
      — plan Step 6 (AC4-response, AC5, AC6, AC7, AC10-client)
- [x] T7. Add `<script src="chatbot/chat.js" defer></script>` before
      `</body>` in `frontend/index.html`, `privacy.html`, `terms.html`,
      `about.html` — one line per page, no other markup change.
      — plan Step 7 (AC1)

## Validate (before code PR — Gate 2)

- [x] T8. Pre-wiring live check with curl against the deployed Function URL:
      covered question → `{"answer", "sources"}` 200; uncovered →
      insufficient-context answer with empty sources; malformed/empty → 4xx
      JSON; `OPTIONS` preflight from
      `Origin: https://ralagiya2053.github.io` → single
      `Access-Control-Allow-Origin` header (confirm no duplicate-header
      regression). Confirms the response shape the widget must render.
      — plan Section 6 (AC10 groundwork)
      Done (2026-10-19, 10-pass battery): `/health` 200; question paths → 200
      `{"answer","sources"}` in 1.3–1.7s; empty/missing/over-length/malformed
      JSON → 422 with `{"detail":"invalid question: ..."}`; preflight from
      https://ralagiya2053.github.io → 200 with exactly ONE
      `access-control-allow-origin` plus allow-headers/methods/max-age
      (no duplicate-header regression); foreign origin → 400 with NO ACAO
      (browser-correct). NOTE (corpus, not contract): the indexed documents
      are still dummy placeholder text, so even "covered" questions get
      LLM-refusal-style answers ("no actual published privacy policy...").
      The widget contract is unaffected; consider replacing the placeholder
      corpus in a follow-up if demo quality matters.
- [ ] T9. Manual checklist on the live GitHub Pages pages (DevTools at
      mobile ≤400px and desktop): FAB placement on all 4 pages; open/close
      mouse + keyboard + Escape; welcome message; send → Thinking… → answer
      with source chips; off-topic → no-chip insufficiency answer; network
      blocked → error bubble + immediate retry; whitespace-only and >1000
      chars rejected without a Network-tab request; live Q&A roundtrip
      succeeds (200, correct CORS, no duplicate ACAO); no horizontal scroll
      or pushed content; visual pass vs F1 tokens/Figma.
      — plan Section 6 table (AC1–AC12)
- [x] T10. Regression: `git diff main…HEAD --name-only` shows zero changes
      under `app/`, `rag-backend/`, both Dockerfiles, and `train/`; frozen
      `/predict` endpoint untouched and unaffected (frontend-only diff).
      — plan Step 8 (AC13)
      Done (2026-10-19): union of committed diff vs main + uncommitted
      working tree + untracked files = changes ONLY in `frontend/` (4 HTML
      pages, styles.css, chat.svg, chatbot/chat.js) and
      `specs/04-chatbot-widget/` — zero changes under `app/`, `rag-backend/`,
      `train/`, either Dockerfile, `.github/`. Live `/predict` regression:
      POST with the frontend's payload shape →
      `{"prediction": 0, "probability": 0.0436…}` HTTP 200 in 3.4s (shape and
      service unchanged; exact probability differs from F3's T12 note because
      that payload wasn't recorded — git evidence of zero frozen-path changes
      is the decisive check).

## Commit & PR (Gate 2)

- [ ] T11. Commit code (`feat: add chatbot widget connecting frontend to F3
      RAG backend (F4, SDD steps 8-10)`) and push. SDD step 10.
- [ ] T12. Open code-review PR against main; CI green; merge after review.
      SDD steps 11–12.