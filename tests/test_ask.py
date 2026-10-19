"""Pytest coverage for the RAG /ask flow (mocked — no AWS credentials needed).

Run via:  .venv/Scripts/python.exe -m pytest tests/test_ask.py
"""

import os
import sys
from pathlib import Path

# Make rag-backend's flat modules importable from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rag-backend"))

os.environ["FRONTEND_ORIGIN"] = "http://testserver"  # before importing main

import main  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from generation import INSUFFICIENT_CONTEXT_ANSWER  # noqa: E402

client = TestClient(main.app)

CHUNKS = [
    {"text": "Placeholder chunk about HbA1c levels.", "source": "policy.md"},
    {"text": "Another placeholder chunk.", "source": "compliance.md"},
    {"text": "Third duplicate-source chunk.", "source": "policy.md"},
]


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "service": "rag"}


def test_ask_happy_path(monkeypatch):
    monkeypatch.setattr(main, "_retrieve", lambda q: CHUNKS)
    seen = {}

    def fake_generate(question, chunks):
        seen["question"] = question
        seen["chunks"] = chunks
        return "HbA1c is a measure of average blood sugar."

    monkeypatch.setattr(main, "_generate", fake_generate)

    resp = client.post("/ask", json={"question": "What is HbA1c?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"] == "HbA1c is a measure of average blood sugar."
    # Sources are de-duplicated document names from the retrieved chunks
    assert body["sources"] == ["policy.md", "compliance.md"]
    assert seen["question"] == "What is HbA1c?"
    assert seen["chunks"] == CHUNKS


def test_ask_no_relevant_chunks_skips_llm(monkeypatch):
    monkeypatch.setattr(main, "_retrieve", lambda q: [])

    def must_not_be_called(*_):
        raise AssertionError("LLM must not be called on empty retrieval")

    monkeypatch.setattr(main, "_generate", must_not_be_called)

    resp = client.post("/ask", json={"question": "Quantum coffee recipes"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"] == INSUFFICIENT_CONTEXT_ANSWER
    assert body["sources"] == []


def test_ask_missing_question(monkeypatch):
    resp = client.post("/ask", json={})
    assert resp.status_code == 422
    assert "detail" in resp.json()


def test_ask_empty_and_whitespace_question(monkeypatch):
    for payload in ({"question": ""}, {"question": "   "}):
        resp = client.post("/ask", json=payload)
        assert resp.status_code == 422
        assert "detail" in resp.json()


def test_ask_over_length_question():
    resp = client.post("/ask", json={"question": "x" * 1001})
    assert resp.status_code == 422


def test_cors_preflight_allowed_origin():
    resp = client.options(
        "/ask",
        headers={
            "Origin": "http://testserver",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.status_code == 200
    assert resp.headers["access-control-allow-origin"] == "http://testserver"


def test_cors_preflight_foreign_origin_blocked():
    resp = client.options(
        "/ask",
        headers={
            "Origin": "https://evil.example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in resp.headers or (
        "evil.example.com" not in resp.headers.get("access-control-allow-origin", "")
    )