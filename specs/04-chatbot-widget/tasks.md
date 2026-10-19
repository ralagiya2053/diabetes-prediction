# Tasks 04 — Chatbot Widget

**Status:** Draft
**Feature ID:** F4
**Branch:** feat/04-chatbot-widget
**Plan:** specs/04-chatbot-widget/plan.md (Approved)
**Created:** 2026-10-19

Tasks map 1:1 to plan Section 5 steps. Mark `- [x]` when done and validated.

## Build

- [ ] T1. Add `frontend/assets/chat.svg` (chat-bubble icon matching the flat
      single-icon SVG pattern of `activity.svg`/`info.svg`) in the F1 accent
      color family. — plan Step 1 (prerequisite for AC1's FAB)
- [ ] T2. Create `frontend/chatbot/chat.js`: inject FAB
      (`<button aria-label="Open chat" aria-expanded>` + `chat.svg`) and panel
      (`role="dialog"`, header + close button, scrollable
      `role="log" aria-live="polite"` messages area, label-associated text
      input, send button) into `document.body` on load; log the welcome
      message on first open; `API_URL` constant at the top of the module as
      the single place the Function URL is configured. — plan Step 2
      (AC1, AC2-markup, AC3)
- [ ] T3. Append a commented `/* F4 — Chatbot widget */` section to
      `frontend/assets/styles.css` consuming existing tokens
      (`--color-accent`, `--radius-card`, `--shadow-card`, Inter): fixed FAB
      bottom-right above footer, ~360×480 desktop card panel,
      `max-width: calc(100vw - 32px)` + capped height with internal scroll at
      small viewports, `prefers-reduced-motion` respected; no existing rule
      edited. — plan Step 3 (AC1, AC11-sizing, AC12)
- [ ] T4. Wire open/close in `chat.js`: toggle FAB/panel, Escape closes,
      close button works, input focused on open, focus returns to FAB on
      close, `aria-expanded` kept in sync. — plan Step 4 (AC2)
- [ ] T5. Implement send flow: submit on send button and Enter in the input;
      trim; whitespace-only → rejected locally (no request); >1000 chars →
      blocked locally with inline warning; user bubble appended, input
      cleared/disabled, "Thinking…" indicator appended. — plan Step 5
      (AC4-client, AC8, AC9)
- [ ] T6. Implement fetch + render in `chat.js`: `POST {API_URL}/ask` with
      `AbortController` (~30s); 200 → answer bubble via `textContent` only
      (no innerHTML with remote text) + source chips omitted when
      `sources` empty (insufficient-context path); 4xx/422 → readable error
      bubble from `detail`; 5xx/network/timeout → friendly retry error
      bubble; indicator replaced and input re-enabled on every outcome.
      — plan Step 6 (AC4-response, AC5, AC6, AC7, AC10-client)
- [ ] T7. Add `<script src="chatbot/chat.js" defer></script>` before
      `</body>` in `frontend/index.html`, `privacy.html`, `terms.html`,
      `about.html` — one line per page, no other markup change.
      — plan Step 7 (AC1)

## Validate (before code PR — Gate 2)

- [ ] T8. Pre-wiring live check with curl against the deployed Function URL:
      covered question → `{"answer", "sources"}` 200; uncovered →
      insufficient-context answer with empty sources; malformed/empty → 4xx
      JSON; `OPTIONS` preflight from
      `Origin: https://ralagiya2053.github.io` → single
      `Access-Control-Allow-Origin` header (confirm no duplicate-header
      regression). Confirms the response shape the widget must render.
      — plan Section 6 (AC10 groundwork)
- [ ] T9. Manual checklist on the live GitHub Pages pages (DevTools at
      mobile ≤400px and desktop): FAB placement on all 4 pages; open/close
      mouse + keyboard + Escape; welcome message; send → Thinking… → answer
      with source chips; off-topic → no-chip insufficiency answer; network
      blocked → error bubble + immediate retry; whitespace-only and >1000
      chars rejected without a Network-tab request; live Q&A roundtrip
      succeeds (200, correct CORS, no duplicate ACAO); no horizontal scroll
      or pushed content; visual pass vs F1 tokens/Figma.
      — plan Section 6 table (AC1–AC12)
- [ ] T10. Regression: `git diff main…HEAD --name-only` shows zero changes
      under `app/`, `rag-backend/`, both Dockerfiles, and `train/`; frozen
      `/predict` endpoint untouched and unaffected (frontend-only diff).
      — plan Step 8 (AC13)

## Commit & PR (Gate 2)

- [ ] T11. Commit code (`feat: add chatbot widget connecting frontend to F3
      RAG backend (F4, SDD steps 8-10)`) and push. SDD step 10.
- [ ] T12. Open code-review PR against main; CI green; merge after review.
      SDD steps 11–12.