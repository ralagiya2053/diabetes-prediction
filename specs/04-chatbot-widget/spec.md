# Spec 04 — Chatbot Widget

**Status:** Approved
**Feature ID:** F4
**Branch:** feat/04-chatbot-widget
**Author:** Rushikesh Alagiya
**Created:** 2026-10-19

## 1. Problem Statement

The F3 RAG backend is deployed and answers questions about the site's policy,
compliance, and charges documents over its `/ask` endpoint, but users can only
reach it by sending requests manually. There is no user-visible way to ask a
question. This feature closes that gap: a chat widget on the website makes the
deployed backend approachable for non-technical visitors and completes the
end-to-end portfolio demo (static site → Lambda RAG → grounded answer).

## 2. Scope

**In scope:**

- A floating action button (FAB) in the bottom-right corner of the frontend:
  the landing page and all three policy pages (privacy, terms, about).
- Clicking the FAB opens a chat panel; clicking again (or a close control)
  closes it. Open/closed state persists while navigating within the same page
  load only.
- The panel contains: a message history area (scrollable), a text input, and a
  send button (input also submits on Enter).
- When the panel is empty, show a brief welcome message inviting the user to
  ask about the site's policies.
- JavaScript that sends the user's question to the deployed F3 RAG backend
  (`POST /ask` on the Lambda Function URL) and renders the answer.
- A visible "Thinking…" loading indicator while a request is in flight.
- Graceful error states: network failure, 5xx (retrieval/generation failure),
  and 4xx validation errors all render a readable message in the chat instead
  of breaking the widget.
- Display of the document sources returned with each answer (e.g., small chips
  or a caption under the bot message).
- Styling consistent with the existing F1 design system (colors, fonts,
  spacing) using the existing stylesheet and vanilla CSS only.
- Basic accessibility: the FAB and input are keyboard-reachable, the panel is
  usable on mobile (full/near-full width within the viewport) and desktop.

**Out of scope:**

- Any change to the RAG backend, its API contract, Lambda configuration, or
  IAM.
- Any change to the prediction service (`/predict`, `/health`).
- Server-side conversation memory or user accounts.
- Streaming responses (answers render once complete).
- Markdown/rich-text rendering of answers (plain text; line breaks preserved).

## 3. User-Facing Behavior

**Before:** all four pages end at their normal content; there is no visible way
to ask questions about the site's policies.

**After:** a round chat bubble (FAB) sits fixed in the bottom-right corner of
every page. Clicking it opens a chat panel above it. A welcome message
invites the user to ask about privacy, terms, charges, or how the predictor
handles their data. The user types a question and presses Enter or the send
button; the message appears in the history, immediately followed by a
"Thinking…" indicator. Within a few seconds, the indicator is replaced by the
assistant's answer, with the source documents it came from shown beneath it.
The answer stays in the history for the rest of the page visit, and the user
can ask more questions. On mobile the panel occupies most of the viewport
width; on desktop it is a card-sized popup above the FAB. Closing the panel
collapses it back to the FAB (history is kept within the page load but is not
restored after navigation or reload).

## 4. Acceptance Criteria

1. The FAB is visible in the bottom-right corner of the landing page and on
   the privacy, terms, and about pages, and does not overlap or obscure
   existing page content or footers.
2. Clicking (or pressing Enter/Space on) the FAB opens the chat panel;
   clicking (or pressing Enter/Space on) the close control closes it.
3. With the panel open, the history area shows a welcome message inviting
   questions about the site's policies.
4. Each user message appears in the history immediately after submission, and
   a loading indicator appears until the backend response arrives, then the
   assistant's answer replaces it.
5. Under each assistant answer that has sources, the source document names
   returned by the backend are displayed.
6. When the backend returns the insufficient-context answer with no sources,
   the widget renders that answer with no source chips and no error.
7. If the backend is unreachable (network failure) or responds 5xx, a readable
   error message appears in the history and the user can immediately try
   again; the widget does not freeze.
8. Empty submissions (whitespace only) are rejected without sending a request.
9. Questions longer than 1000 characters are blocked client-side with a
   warning, without sending a request.
10. Requests are sent to the deployed F3 `/ask` endpoint and succeed end-to-end
    from the GitHub Pages origin (CORS passes; answers visible on the live
    site).
11. The widget renders and functions correctly at mobile viewport widths
    (≤ 400px CSS width) and desktop widths, verified manually on live pages.
12. The widget's look (colors, typography, corner radii) matches the existing
    F1 design tokens defined in the site stylesheet; no third-party CSS or JS
    framework is introduced.
13. The prediction service, RAG backend code, Dockerfiles, and training data
    are unmodified (`git diff` against main shows no changes to those paths).

## 5. Non-Goals

- Multi-turn conversation context: follow-ups are handled as independent
  questions, matching the deployed single-question `/ask` contract. If a user
  asks "why?" as a follow-up, the backend may return an insufficient-context
  answer; handling that gracefully is in scope, true multi-turn memory is not.
- Persisting chat history across page loads, navigation, or sessions.
- File uploads, voice input, or attachments.
- Analytics/telemetry on widget usage.
- Rate limiting or abuse prevention beyond client-side validation.
- Internationalization (English only).

## 6. Dependencies

- **F3 (merged):** deployed RAG Lambda Function URL and its API contract
  (`POST /ask` accepting `{"question": "…"}` and returning
  `{"answer": "…", "sources": [...]}`; 4xx/5xx as JSON `{"detail": "…"}`).
  CORS on the deployed backend allows the GitHub Pages origin.
- **F1 (merged):** Figma design and design tokens in the existing stylesheet,
  which the widget reuses for visual consistency.
- **Files this feature will touch (new or lightly extended):**
  - the four HTML pages (adding the widget markup/include),
  - the existing stylesheet (widget styles appended),
  - new frontend files: widget JS and widget-specific asset/icon if needed.
- **Frozen files:** none are modified. All changes are additive to the
  frontend; the backend is consumed read-only over HTTP.

## 7. Risks & Unknowns

- **Cold-start latency:** a Lambda cold start plus a Bedrock call can take
  several seconds; the loading indicator must make this feel intentional
  rather than broken. Timeout for the fetch should be generous (~30s) with a
  clear error after that.
- **Insufficient-context answers** ("I don't have information about…") could
  be mistaken for a bug by users — the welcome message should set expectations
  that the assistant knows the site's policy documents.
- **Function URL hard-coded in frontend JS:** if the Lambda URL changes, the
  widget breaks silently. Mitigate by keeping the endpoint in exactly one
  configuration place in the widget code.
- **Duplicate CORS preflight headers** would break the widget from the live
  origin; the backend is already configured to avoid this (Function URL CORS
  disabled), but validation must be done against the live site, not localhost.
- **Panel height on small screens:** must not force horizontal scroll or push
  page content; needs explicit small-viewport sizing rules.

## 8. Open Questions

- Resolved by user scope statement: widget on all four pages; sources
  displayed; loading/error states required; no new frameworks.
- None remaining that block plan.md. (If the team later wants true multi-turn
  memory, that would be a new F3 backend feature, not part of F4.)

## 9. References

- Figma design (F1): existing Figma link used for the page redesign (see
  `specs/01-website-ui-links/spec.md`).
- F3 spec and runbook: `specs/03-rag-backend/spec.md`, `RUNBOOK.md` —
  live endpoint `https://kvjinvbq37vl2k5gh45xcaj2e40hpldn.lambda-url.us-east-1.on.aws/`.
- RAG API contract: `rag-backend/README.md` and `rag-backend/schema.py`.
- Deployed site: https://ralagiya2053.github.io/diabetes-prediction/frontend/index.html