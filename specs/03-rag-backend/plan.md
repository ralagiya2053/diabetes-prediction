# Plan 03 — RAG Backend

**Status:** Draft
**Feature ID:** F3
**Branch:** feat/03-rag-backend
**Spec:** specs/03-rag-backend/spec.md (Approved)
**Author:** Rushikesh Alagiya
**Created:** 2026-10-18

## 1. Approach Summary
Build a self-contained FastAPI service in a new `rag-backend/` directory that
serves `POST /ask` (question → grounded answer + sources) and `GET /health`,
mirroring the frozen prediction service's stack: Python 3.11 + FastAPI in a
Docker image with AWS Lambda Web Adapter, pushed to a new ECR repository and
attached to a new Lambda Function URL via console (no SAM/CDK). Retrieval uses
Amazon Titan Text Embeddings V2 (`amazon.titan-embed-text-v2:0`, 1024-dim)
against an S3 Vectors index; generation uses Claude 3 Haiku
(`anthropic.claude-3-haiku-20240307-v1:0`) via Bedrock Converse with a
strict ground-in-context prompt that refuses to answer when retrieval returns
nothing relevant (explicit insufficient-context response instead). A small
markdown corpus (3–5 files: policy, compliance, charges) lives in
`rag-backend/documents/` and is ingested by a repeatable script. CORS is
enforced at the app level for the GitHub Pages origin only. All Python
dependencies are installed in the project `.venv`, never globally.

## 2. Files to Create
All new; nothing in frozen directories or `frontend/`:
- `rag-backend/main.py` — FastAPI app: `/ask`, `/health`, CORS middleware,
  endpoint wiring
- `rag-backend/schema.py` — Pydantic models: AskRequest (`question`)
  / AskResponse (`answer`, `sources` list)
- `rag-backend/retrieval.py` — embed question with Titan Embeddings V2
  (Bedrock Runtime), query S3 Vectors index, return top-k chunks + source docs
- `rag-backend/generation.py` — Bedrock Converse call to Claude 3 Haiku with
  grounding system prompt and insufficient-context handling
- `rag-backend/ingest.py` — CLI script: chunk `documents/*.md` by section
  headings, embed chunks in batches, upsert into the S3 Vectors index with
  source-document metadata (idempotent re-runs replace index state)
- `rag-backend/documents/` — corpus: `charges.md`, `compliance.md`,
  `policy.md` (dummy marketing/FAQ-style text, agreed sample set)
- `rag-backend/Dockerfile` — same Lambda Web Adapter pattern as the frozen
  service (copied as reference, adapted paths)
- `rag-backend/requirements.txt` — fastapi, uvicorn, boto3, pydantic
- `rag-backend/README.md` — deployment + ingestion runbook (console steps,
  env vars, IAM policy JSON for the Lambda role)
- `tests/test_ask.py` — pytest: happy path + malformed request, mocking
  Bedrock/S3 Vectors calls
- New dependencies to install in `.venv` (dev/test only): `pytest`, `httpx`;
  runtime deps (`fastapi`, `uvicorn`, `boto3`, `pydantic`) are listed above
  and also installed in `.venv` — never global, per user constraint

## 3. Files to Modify
- `tests/` — one new file appended to the existing pytest suite
  (`tests/test_ask.py`); existing `tests/test_predict.py` untouched
- No frozen files (`app/`, `Dockerfile`, model artifacts,
  `train/diabetes.csv`), no `frontend/`, no `.github/` changes
- AWS resources (console-created, documented in `rag-backend/README.md`):
  ECR repo, S3 vector bucket + vector index, Lambda function + Function URL
  (auth: NONE), IAM execution role

## 4. Architecture / Data Flow
```
Browser/API client (origin https://ralagiya2053.github.io)
        │ POST /ask {"question": "..."}
        ▼
Lambda Function URL (auth NONE) ── Lambda Web Adapter ── FastAPI on :8080
        │ (rag-backend/main.py)
        ├─ validate question (4xx on empty/>max-length)
        ├─ Titan Embeddings V2 ── bedrock-runtime invoke ──▶ vector (1×1024)
        ├─ S3 Vectors query top-k (k≈3) ──▶ chunks + metadata {source}
        │      └─ empty/irrelevant? ──▶ 200 {"answer": "insufficient context...", "sources": []}
        ├─ Claude 3 Haiku (Bedrock Converse)
        │      system: answer ONLY from supplied context; cite documents
        │      user: context chunks + question
        └─ 200 {"answer": "...", "sources": ["doc1.md", ...]}
GET /health ──▶ 200 {"status": "ok", "service": "rag", ...}
```
Deployment (console, per existing pattern):
```
docker build (rag-backend/) ──▶ push ECR ──▶ new Lambda (image, Web Adapter
layer) ──▶ IAM role: bedrock:InvokeModel/Converse + s3vectors:Query/PutVectors
──▶ Function URL auth NONE ──▶ app-level CORS allow-origin github.io
```
CORS decision: enforced by FastAPI `CORSMiddleware` in the app (locally
testable), Function URL CORS setting DISABLED — enabling both would emit
duplicate Access-Control-Allow-Origin headers and break preflight.

## 5. Step-by-Step Implementation
1. Scaffold `rag-backend/`: `main.py` (FastAPI + `/health`), `schema.py`,
   `requirements.txt`; install runtime + test deps in `.venv`; smoke-run
   `uvicorn` locally. — satisfies (setup for AC1, AC6, AC10)
2. Write `retrieval.py`: Titan V2 embed + S3 Vectors top-k query with source
   metadata. — satisfies AC1, AC7, AC12 structure
3. Write `generation.py`: Claude 3 Haiku via Converse, grounded system
   prompt; when retrieved chunks are empty/below relevance bar, return the
   explicit insufficient-context answer with empty sources and skip the LLM
   call. — satisfies AC2, AC3
4. Wire `POST /ask` in `main.py`: request validation (empty/missing/over-
   length → 4xx JSON error), CORS middleware restricted to
   `https://ralagiya2053.github.io`. — satisfies AC1, AC3 (4xx path), AC5
5. Write corpus (`rag-backend/documents/`: charges.md, compliance.md,
   policy.md) and `ingest.py` chunker/uploader; run once to fill the S3
   Vectors index (vector bucket/index names pinned in README), re-run to
   confirm idempotency. — satisfies AC11
6. Add `rag-backend/Dockerfile` mirroring the frozen service's Lambda Web
   Adapter pattern (port 8080, adapted paths). — satisfies AC1 (deployment
   path), AC9 config
7. Local validation: `tests/test_ask.py` (happy path, malformed request —
   Bedrock/S3 Vectors mocked) passing in `.venv`; local runbook curl checks
   against `uvicorn` (200 answer with sources, 4xx paths, insufficient-
   context path with empty corpus mock, OPTIONS preflight). — satisfies
   AC3, AC4, AC10
8. Deploy to AWS: create ECR repo, build+push image (us-east-1), create
   Lambda + Web Adapter layer + IAM role (bedrock invoke + s3vectors
   permissions on the specific bucket/index), verify Bedrock model access
   for both models (open access request if not already enabled), create
   Function URL, record everything in `rag-backend/README.md`. — satisfies
   AC6 (deployed), AC7, AC12
9. Live verification with curl: `/health` 200; `/ask` covered question →
   answer + sources; uncovered question → explicit insufficient-context;
   empty/over-length → 4xx; preflight from
   `Origin: https://ralagiya2053.github.io` succeeds; time both `/ask`
   variants against the 10s ceiling. — satisfies AC1–AC5, AC9
10. Regression pass: call the existing `/predict` endpoint with the current
    frontend payload and confirm response identical to pre-F3. — satisfies
    AC8

Suggested commit messages (SDD step referenced):
- Steps 1–5: `feat: add RAG service skeleton, retrieval, generation, and corpus (F3, Gate 1 spec merged, SDD step 8)`
- Step 6–7: `test: add mocked pytest coverage for /ask happy and error paths (F3, SDD step 9)`
- Step 8–10: `docs: add RAG backend deploy runbook after live verification (F3, SDD step 10)`

## 6. Test Strategy
- Automated (`tests/test_ask.py`, mocked, no AWS credentials needed).
  - happy path: question → 200 `{answer, sources: [doc,...]}`
  - no-relevant-chunks: → 200 with explicit insufficient-context answer,
    empty sources, LLM not called
  - malformed: missing `question`, empty string, over-length → 4xx
  - health: `/health` 200
- Manual (local): runbook curls against `uvicorn` incl. OPTIONS preflight.
- Manual (live, post-deploy, step 9): the same curl battery against the
  Function URL + latency timing (target ≤10s, expectation ~3s) + one
  regression call to the frozen `/predict` endpoint (AC8).
- AC map:
  - AC1, AC4 → steps 4, 7, 9
  - AC2 → steps 3, 5, 7, 9
  - AC3 → steps 3, 7, 9
  - AC5 → steps 4, 7, 9
  - AC6 → steps 1, 8, 9
  - AC7 → steps 2, 3, 8
  - AC8 → step 10
  - AC9 → steps 6, 9
  - AC10 → steps 1, 7
  - AC11 → step 5
  - AC12 → steps 2, 5, 8

## 7. Rollout & Rollback
- **Deploy:** new ECR image → new Lambda (console, steps in README) → new
  Function URL. Predictive service untouched; nothing in `frontend/` links
  to `/ask` yet (F4 does), so the blast radius of any defect is the API
  surface only.
- **Rollback:** point the F3 Lambda to the previous image digest in console
  (revert of a bad image), or delete the F3 Lambda/s3 vector bucket entirely
  — no shared state with the prediction service. Code revert: `git revert`
  on this branch; AWS-side objects are additive and removable.
- The S3 Vectors bucket/index can be recreated deterministically via
  `ingest.py` (AC11) if the store is corrupted.

## 8. Risks & Mitigations
- **Bedrock model access not enabled** for Titan Embeddings V2 or Claude 3
  Haiku → checked early (step 8 preamble) with fallback: request open access
  in console, which is instant for most us-east-1 models.
- **Duplicate CORS headers** if both Function URL config and app middleware
  add headers → CORS implemented only in app middleware (explicit decision
  in Section 4); preflight verified from the real frontend origin.
- **S3 Vectors dimension/limit mismatch** (index fixed at 1024 to match
  Titan V2 default) → dimension constant defined once, shared by `ingest.py`
  and `retrieval.py`; a change requires full re-ingest, which is
  deterministic and cheap at this corpus size.
- **Slow RAG path vs Lambda/Web Adapter settings** → Function URL timeout
  set generously (30s) while the app targets ≤10s; latency measured live in
  step 9.
- **Dummy corpus makes demo answers weak** → corpus files written to be
  meaningful-but-clearly-sample content (policy/compliance/charges topics)
  so retrieval hits produce sensible grounded answers.
- **Global pip installs during dev** → hard rule: all installs via
  `.venv/Scripts/python.exe -m pip`; no `python -m pip` outside `.venv`.

## 9. Open Questions
None.