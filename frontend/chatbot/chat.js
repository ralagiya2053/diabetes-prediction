/* ============================================================
   F4 — Chatbot widget (specs/04-chatbot-widget)
   Vanilla-JS module; injects the FAB + chat panel into the page.
   Loaded on all four pages via <script src="chatbot/chat.js" defer>.
   ============================================================ */

(function () {
  "use strict";

  // Single place the F3 RAG backend endpoint is configured (plan Section 8 risk).
  var API_URL = "https://kvjinvbq37vl2k5gh45xcaj2e40hpldn.lambda-url.us-east-1.on.aws/ask";

  var FETCH_TIMEOUT_MS = 30000; // generous: cold start + Bedrock latency
  var QUESTION_MAX_CHARS = 1000; // mirrors the backend AskRequest contract

  var WELCOME_TEXT =
    "Hi! I'm the site assistant. Ask me about our privacy policy, " +
    "terms of service, about us, or how this site handles charges and " +
    "compliance.";

  // The widget is self-injecting; guard in case the script is ever loaded twice.
  if (document.getElementById("chat-fab")) return;

  /* ---------------- DOM construction helpers ---------------- */

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function svgIcon(src, altText) {
    var img = document.createElement("img");
    img.src = src;
    img.alt = altText || "";
    return img;
  }

  /* ---------------- FAB ---------------- */

  var fab = el("button", "chatbot__fab");
  fab.id = "chat-fab";
  fab.type = "button";
  fab.setAttribute("aria-label", "Open chat");
  fab.setAttribute("aria-haspopup", "dialog");
  fab.setAttribute("aria-expanded", "false");
  fab.appendChild(svgIcon("assets/chat.svg", ""));

  /* ---------------- Panel ---------------- */

  var panel = el("div", "chatbot__panel");
  panel.id = "chat-panel";
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-label", "Assistant chat");
  panel.hidden = true;
  // .chatbot__panel's `display: flex` beats the UA stylesheet's
  // [hidden] { display: none }, so hidden alone never hides the panel —
  // toggle style.display alongside it (bug found in F4 build review).
  panel.style.display = "none";

  var header = el("div", "chatbot__head");
  var headerTitle = el("p", "chatbot__head-title", "Assistant");
  var headerHint = el("p", "chatbot__head-hint", "Grounded in site policy documents");
  var closeBtn = el("button", "chatbot__close");
  closeBtn.type = "button";
  closeBtn.setAttribute("aria-label", "Close chat");
  closeBtn.appendChild(svgIcon("assets/chevron-down.svg", ""));
  header.appendChild(headerTitle);
  header.appendChild(headerHint);
  header.appendChild(closeBtn);

  var messages = el("div", "chatbot__messages");
  messages.setAttribute("role", "log");
  messages.setAttribute("aria-live", "polite");

  var form = el("form", "chatbot__form");

  var inputLabel = el("label", "chatbot__input-label", "Ask a question");
  inputLabel.setAttribute("for", "chat-input");

  var input = el("input", "chatbot__input");
  input.id = "chat-input";
  input.type = "text";
  input.name = "question";
  input.autocomplete = "off";
  input.placeholder = "Type your question…";
  input.setAttribute("maxlength", String(QUESTION_MAX_CHARS * 2)); // hard stop for pastes; custom warning covers the 1000 rule

  var sendBtn = el("button", "chatbot__send");
  sendBtn.type = "submit";
  sendBtn.setAttribute("aria-label", "Send message");
  sendBtn.appendChild(svgIcon("assets/arrow-right.svg", ""));

  var hint = el("p", "chatbot__hint"); // inline warning text (empty / over-length)
  hint.hidden = true;
  hint.setAttribute("role", "alert");

  form.appendChild(inputLabel);
  form.appendChild(input);
  form.appendChild(hint);
  form.appendChild(sendBtn);

  panel.appendChild(header);
  panel.appendChild(messages);
  panel.appendChild(form);

  /* ---------------- Message rendering ----------------
     All backend-provided text goes in via textContent/createElement only —
     no innerHTML with remote content (plan Section 8, XSS risk). */

  function showWelcome() {
    messages.appendChild(el("div", "chatbot__bubble chatbot__bubble--bot", WELCOME_TEXT));
  }

  function addUserMessage(text) {
    messages.appendChild(el("div", "chatbot__bubble chatbot__bubble--user", text));
    scrollToBottom();
  }

  function addBotMessage(text) {
    var bubble = el("div", "chatbot__bubble chatbot__bubble--bot", text);
    messages.appendChild(bubble);
    scrollToBottom();
    return bubble;
  }

  function addThinkingIndicator() {
    var bubble = el("div", "chatbot__bubble chatbot__bubble--bot chatbot__bubble--thinking", "Thinking…");
    messages.appendChild(bubble);
    scrollToBottom();
    return bubble;
  }

  function addBotAnswerWithSources(answer, sources) {
    var bubble = addBotMessage(answer);
    if (sources && sources.length) {
      var row = el("div", "chatbot__sources");
      row.appendChild(el("span", "chatbot__sources-label", "Sources:"));
      for (var i = 0; i < sources.length; i++) {
        row.appendChild(el("span", "chatbot__source-chip", sources[i]));
      }
      bubble.appendChild(row);
    }
  }

  function addErrorBubble(text) {
    var bubble = el("div", "chatbot__bubble chatbot__bubble--error", text);
    messages.appendChild(bubble);
    scrollToBottom();
    return bubble;
  }

  function scrollToBottom() {
    messages.scrollTop = messages.scrollHeight;
  }

  function showHint(text) {
    hint.textContent = text;
    hint.hidden = false;
  }

  function clearHint() {
    hint.textContent = "";
    hint.hidden = true;
  }

  /* ---------------- Open / close (AC2, AC3) ---------------- */

  var openedOnce = false;

  function setExpanded(expanded) {
    fab.setAttribute("aria-expanded", expanded ? "true" : "false");
  }

  function openPanel() {
    panel.hidden = false;
    panel.style.display = "flex";
    setExpanded(true);
    fab.setAttribute("aria-label", "Close chat");
    if (!openedOnce) {
      showWelcome();
      openedOnce = true;
    }
    input.focus();
    scrollToBottom();
  }

  function closePanel() {
    panel.hidden = true;
    panel.style.display = "none";
    setExpanded(false);
    fab.setAttribute("aria-label", "Open chat");
    fab.focus();
  }

  fab.addEventListener("click", function () {
    if (panel.hidden) openPanel();
    else closePanel();
  });

  closeBtn.addEventListener("click", closePanel);

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !panel.hidden) closePanel();
  });

  /* ---------------- Send flow + client validation (AC4, AC8, AC9) ---------------- */

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    clearHint();

    var question = input.value.trim();

    if (!question) {
      showHint("Please type a question before sending.");
      return;
    }
    if (question.length > QUESTION_MAX_CHARS) {
      showHint(
        "Questions are limited to " + QUESTION_MAX_CHARS +
        " characters. Please shorten your question (" +
        question.length + " characters entered)."
      );
      return;
    }

    input.value = "";
    addUserMessage(question);
    sendQuestion(question);
  });

  function setPending(isPending) {
    input.disabled = isPending;
    sendBtn.disabled = isPending;
    if (!isPending) input.focus();
  }

  function sendQuestion(question) {
    setPending(true);
    var indicator = addThinkingIndicator();

    // AbortController with a generous timeout for Lambda cold start (plan Section 8).
    var controller = new AbortController();
    var timeoutId = setTimeout(function () {
      controller.abort();
    }, FETCH_TIMEOUT_MS);

    fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question }),
      signal: controller.signal,
    })
      .then(function (response) { return handleResponse(response, indicator); })
      .catch(function (error) { handleFetchError(error, indicator); })
      .finally(function () {
        clearTimeout(timeoutId);
        setPending(false);
      });
  }

  /* ---------------- Response handling (AC4, AC5, AC6, AC7) ---------------- */

  function handleResponse(response, indicator) {
    if (indicator.parentNode) indicator.parentNode.removeChild(indicator);

    if (response.ok) {
      return response.json()
        .then(function (data) {
          addBotAnswerWithSources(data.answer || "(empty answer)", data.sources || []);
        });
    }

    // 4xx JSON detail path (e.g. 422 "invalid question: ...")
    return response.json()
      .then(function (data) {
        addErrorBubble("The assistant could not process that: " + (data.detail || ("HTTP " + response.status)) + ".");
      })
      .catch(function () {
        addErrorBubble("The assistant could not process that (HTTP " + response.status + ").");
      });
  }

  function handleFetchError(error, indicator) {
    if (indicator.parentNode) indicator.parentNode.removeChild(indicator);

    if (error && error.name === "AbortError") {
      addErrorBubble("The assistant took too long to respond, possibly a cold start. Please try again.");
      return;
    }
    // Network/server failure: 5xx path or unreachable backend (AC7, AC10).
    addErrorBubble(
      "The assistant is unavailable right now. Please try again in a moment."
    );
  }

  /* ---------------- Injection ---------------- */

  document.body.appendChild(fab);
  document.body.appendChild(panel);
})();