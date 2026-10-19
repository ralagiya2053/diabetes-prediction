# RAG Backend (F3)

Question-answering service: `POST /ask` embeds the question with Amazon Titan
Text Embeddings V2, retrieves top-3 chunks from an S3 Vectors index, and
generates a grounded answer with Claude 3 Haiku (Bedrock Converse). Empty or
irrelevant retrieval returns an explicit insufficient-context answer without
calling the LLM. `GET /health` reports service readiness.

Additive to the frozen prediction service — see `specs/03-rag-backend/plan.md`.

## Runtime configuration (env vars)

| Variable | Required | Purpose |
|----------|----------|---------|
| `VECTOR_BUCKET_NAME` | yes | S3 vector bucket holding the index |
| `VECTOR_INDEX_NAME` | yes | vector index inside the bucket |
| `EMBED_MODEL_ID` | no (default `amazon.titan-embed-text-v2:0`) | Bedrock embedding model |
| `EMBED_DIM` | no (default `1024`) | Titan V2 output dimension |
| `LLM_MODEL_ID` | no (default `anthropic.claude-3-haiku-20240307-v1:0`) | Bedrock LLM |
| `AWS_REGION` | no (default `us-east-1`) | AWS region (guardrail: us-east-1 only) |
| `FRONTEND_ORIGIN` | no (default `https://ralagiya2053.github.io`) | CORS allow-origin |

## Local development

Python dependencies go in the project `.venv` only — never install globally:

    .venv/Scripts/python.exe -m pip install -r rag-backend/requirements.txt
    .venv/Scripts/python.exe -m pytest tests/test_ask.py
    .venv/Scripts/python.exe -m uvicorn main:app --app-dir rag-backend --port 8080

(CORS locally: unset `FRONTEND_ORIGIN` for localhost testing — the GitHub
origin restriction only matters for the deployed URL.)

## Deployment (console, no IaC — same pattern as the prediction service)

1. **Bedrock model access:** in the Bedrock console (us-east-1), confirm
   *Amazon Titan Text Embeddings V2* and *Claude 3 Haiku* are enabled for the
   account (Request model access first if not).
2. **S3 Vectors:** create vector bucket + index — index dimension **1024**,
   distance metric **COSINE** (Titan V2 is normalized).
3. **ECR:** create repo `rag-backend` (us-east-1), then:
       docker build -t rag-backend rag-backend/
       docker tag rag-backend:latest <ecr-url>/rag-backend:latest
       docker push <ecr-url>/rag-backend:latest
4. **Lambda:** create function from container image; Lambda Web Adapter is
   baked into the image (`AWS_LWA_PORT=8080`), timeout **30s** (app targets
   ≤10s), memory 512 MB.
5. **IAM execution role:** `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`,
   `s3vectors:QueryVectors`, `s3vectors:PutVectors` scoped to the specific
   bucket/index + bedrock model IDs — see the policy JSON below.
6. **Function URL:** enable with auth type `NONE`; leave the URL's CORS
   setting **DISABLED** — CORS is enforced by the app's middleware and both
   layers enabled would emit duplicate headers and break preflight.
7. **Set env vars** on the Lambda for `VECTOR_BUCKET_NAME`, `VECTOR_INDEX_NAME`.

## Ingestion (idempotent — AC11)

    VECTOR_BUCKET_NAME=<bucket> VECTOR_INDEX_NAME=<index> \
      .venv/Scripts/python.exe rag-backend/ingest.py

Chunks each `rag-backend/documents/*.md` on `## ` headings and upserts
vectors keyed `{doc}::{n}`; re-runs replace state deterministically at this
corpus size. `ingest.py` does not delete keys from removed documents — use
`list_vectors` manually if the corpus shrinks.

## IAM actions for the Lambda execution role (JSON snippets)

    {
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
      "Resource": [
        "arn:aws:bedrock:*:<account>:foundation-model/amazon.titan-embed-text-v2:0",
        "arn:aws:bedrock:*:<account>:foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["s3vectors:QueryVectors", "s3vectors:PutVectors"],
      "Resource": ["arn:aws:s3vectors:*:<account>:bucket/<bucket>"]
    }

## API contract

    POST /ask        {"question": "<1..1000 chars>"} → {"answer": "...", "sources": ["policy.md", ...]}
    GET  /health     → {"status": "ok", "service": "rag"}
    422/4xx          → {"detail": "invalid question: ..."}