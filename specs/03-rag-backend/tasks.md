# Tasks 03 — RAG Backend

**Status:** Draft
**Feature ID:** F3
**Branch:** feat/03-rag-backend
**Plan:** specs/03-rag-backend/plan.md (Approved)
**Created:** 2026-10-18

Tasks map 1:1 to plan Section 5 steps. Mark `- [x]` when done and validated.

## Build

- [x] T1. Scaffold `rag-backend/`: `main.py` (FastAPI + `/health`), `schema.py`
      (AskRequest/AskResponse), `requirements.txt`; install runtime + test
      deps via `.venv/Scripts/python.exe -m pip` ONLY (never global); smoke-run
      `uvicorn` locally. — plan Step 1 (sets up AC1, AC6, AC10)
- [x] T2. Write `rag-backend/retrieval.py`: Titan Embeddings V2
      (`amazon.titan-embed-text-v2:0`) embed + S3 Vectors top-3 query
      returning chunks with source-document metadata. — plan Step 2
      (AC1, AC7, AC12)
- [x] T3. Write `rag-backend/generation.py`: Claude Haiku 5.5 via Bedrock
      Converse with grounding system prompt; empty/irrelevant retrieval →
      explicit insufficient-context answer, empty sources, no LLM call.
      — plan Step 3 (AC2, AC3)
- [x] T4. Wire `POST /ask` in `main.py`: validation (empty/missing/over-length
      → 4xx JSON error), CORS middleware restricted to
      `https://ralagiya2053.github.io` only (Function URL CORS stays
     DISABLED). — plan Step 4 (AC1, AC3-4xx, AC5)
- [x] T5. Write corpus and ingestion: `rag-backend/documents/{charges.md,
      compliance.md, policy.md}` (dummy but sensible sample text) +
      `rag-backend/ingest.py` (section-chunking, batched embed, idempotent
      S3 Vectors upsert); run once to fill the index, re-run to verify
      determinism. — plan Step 5 (AC11)
- [x] T6. Add `rag-backend/Dockerfile` mirroring the frozen service's Lambda
      Web Adapter pattern (port 8080, adapted paths only). — plan Step 6
      (AC1 deploy path, AC9 timeout config)
- [x] T7. Write `tests/test_ask.py` (in `.venv`, mocks for Bedrock/S3
      Vectors): happy path, no-relevant-chunks path, three malformed
      variants, `/health`; run locally green. — plan Step 7 (AC3, AC4, AC10)
- [x] T8. Write `rag-backend/README.md` runbook: console deploy steps, pinned
      vector bucket/index + model IDs, env vars, IAM policy JSON for the
      Lambda role, ingest instructions. — plan Step 8 supporting material

## Validate (before code PR — Gate 2)

- [ ] T9. Manual local runbook checks with curl against `uvicorn`: 200 answer
      + sources; insufficient-context path; empty/missing/over-length → 4xx;
      OPTIONS preflight with `Origin: https://ralagiya2053.github.io`; no
      un-restricted origin allowed. — plan Step 7 (AC1, AC3, AC4, AC5)
- [ ] T10. Deploy to AWS (us-east-1 only): ECR repo + push, Lambda with Web
      Adapter layer, IAM role with bedrock invoke + s3vectors permissions,
      Function URL (auth NONE, CORS DISABLED); confirm Bedrock model access
      first for both models. — plan Step 8 (AC6, AC7, AC12)
      Progress (2026-10-19): ECR repo created + image pushed (digest
      sha256:38e3b30b…); Lambda `rag-backend` Active (512MB/30s, env vars set);
      role `rag-backend-lambda-role` inline policy (logs, ECR pull, bedrock
      invoke, s3vectors); Function URL auth NONE + CORS disabled + public
      invoke permission added. BLOCKED: account under AWS verification —
      Bedrock InvokeModel and anonymous Function-URL access both denied;
      /health returns 403 until verification clears. Remaining: re-run ingest
      (T5 live half), model-access enablement if still needed, then complete
      this task.
- [ ] T11. Live verification with curl against the Function URL: `/health`
      200; covered question → answer+sources; uncovered question → explicit
      insufficient-context; malformed → 4xx; preflight from frontend origin;
      time `/ask` (ceiling 10s, expected ~3s). — plan Step 9 (AC1–AC5, AC9)
- [ ] T12. Regression: call existing frozen `/predict` endpoint with a
      current frontend payload; confirm response identical to pre-F3.
      — plan Step 10 (AC8)

## Commit & PR (Gate 2)

- [ ] T13. Commit code (`feat: add RAG backend service with retrieval and
      generation (F3, SDD steps 9-10)`) and push. SDD step 10.
- [ ] T14. Open code-review PR against main; CI green; merge after review.
      SDD steps 11–12. — plan Step 7 commit sequence