# RAG Backend (F3)

Question-answering service: `POST /ask` embeds the question with Amazon Titan
Text Embeddings V2, retrieves top-3 chunks from an S3 Vectors index, and
generates a grounded answer with Claude Haiku 5.5 (Bedrock Converse). Empty or
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
| `LLM_MODEL_ID` | no (code default `us.anthropic.claude-haiku-5-5`; deployed instance currently overrides to `us.anthropic.claude-haiku-4-5-20251001-v1:0` until Haiku 5.5 model access is granted) | Bedrock LLM (inference-profile ID) |
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
   *Amazon Titan Text Embeddings V2* and *Claude Haiku 5.5* are enabled for the
   account (Request model access first if not).
   Gotchas learned at deploy time:
   - Newer Anthropic models are not invocable directly (on-demand throughput
     unsupported) — use the **system-defined cross-region inference profile**
     ID (`us.<model-id>`, listed by `aws bedrock list-inference-profiles`).
   - IAM must allow `bedrock:InvokeModel` on the profile ARN
     (`arn:aws:bedrock:<region>:<account>:inference-profile/<id>`) AND on the
     underlying foundation-model ARNs in **every routing region** the profile
     can fan out to (for `us.` profiles: us-east-1, us-east-2, us-west-2).
2. **S3 Vectors:** create vector bucket + index — index dimension **1024**,
   distance metric **COSINE** (Titan V2 is normalized).
3. **ECR:** create repo `rag-backend` (us-east-1), then:
       docker build -t rag-backend rag-backend/
       docker tag rag-backend:latest 974443623644.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest
       docker push 974443623644.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest
   (Repo created 2026-10-19: tag-pushed `latest` = sha256:53c7e94a…f87cf6817fa639.)
4. **Lambda:** create function from container image; Lambda Web Adapter is
   baked into the image (`AWS_LWA_PORT=8080`), timeout **30s** (app targets
   ≤10s), memory 512 MB. CLI gotcha: build/push with
   `docker build --provenance=false --sbom=false` or Lambda rejects the OCI
   manifest list ("image manifest ... not supported"). Deployed (2026-10-19):
   function `rag-backend` from ECR digest `sha256:38e3b30b…0afae315`.
5. **IAM execution role:** `rag-backend-lambda-role` — inline policy
   `rag-backend-inline` covering CloudWatch logs, ECR pull, `bedrock:InvokeModel`
   / +ResponseStream scoped to the two model IDs, and on the vector bucket AND
   index ARNs (`…/bucket/<bucket>` and `…/bucket/<bucket>/index/<index>`):
   `s3vectors:QueryVectors`, `s3vectors:GetVectors` (required with
   `returnMetadata=true`), `s3vectors:PutVectors`, `s3vectors:ListVectors`.
   Lambda caches its role credentials per sandbox — after an IAM policy
   change, force a refresh with a no-op
   `update-function-configuration --environment` call.
   (Account-managed policies like `AWSLambdaBasicExecutionRole` could not be
   referenced in this account at deploy time, so everything is inline.)
6. **Function URL:** enable with auth type `NONE`; leave the URL's CORS
   setting **DISABLED** — CORS is enforced by the app's middleware and both
   layers enabled would emit duplicate headers and break preflight.
   CLI gotcha: `create-function-url-config` adds no public invoke permission
   (the console auto-adds them) — **both** of these statements are required,
   each alone still 403s anonymous callers:
       aws lambda add-permission --function-name rag-backend \
         --statement-id FunctionURLAllowPublicAccess \
         --action lambda:InvokeFunctionUrl --principal "*" \
         --function-url-auth-type NONE
       aws lambda add-permission --function-name rag-backend \
         --statement-id FunctionURLInvokeAllowPublicAccess \
         --action lambda:InvokeFunction --principal "*" \
         --invoked-via-function-url
   Live URL: `https://kvjinvbq37vl2k5gh45xcaj2e40hpldn.lambda-url.us-east-1.on.aws/`
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
        "arn:aws:bedrock:*:<account>:foundation-model/anthropic.claude-haiku-5-5"
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