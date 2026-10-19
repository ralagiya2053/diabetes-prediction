# Spec 03 — RAG Backend

**Status:** Approved
**Feature ID:** F3
**Branch:** feat/03-rag-backend
**Author:** Rushikesh Alagiya
**Created:** 2026-10-18

## 1. Problem Statement
The site can predict diabetes risk from measurements, but it cannot answer
questions about diabetes itself — a visitor who asks "what is HbA1c?" or "how
is my hypertension reading used?" leaves the site. The portfolio demo also
needs a retrieval-augmented component: grounding answers in project-owned
documents instead of raw model output, which both improves answer quality and
demonstrates a second AWS AI workload. F3 builds the backend that answers
natural-language questions by retrieving relevant chunks from a document store
and generating a grounded answer with a Bedrock LLM. The chat widget that uses
it is a separate feature (F4).

## 2. Scope
**In scope:**
- A new, separate Lambda-backed HTTP endpoint (additive — the existing
  prediction service stays frozen and untouched).
- A question-answering flow: embed the incoming question, retrieve the most
  relevant document chunks, and generate an answer with a LLM grounded in
  those chunks.
- A vector index of project-owned diabetes-related documents in S3 Vectors
  (per the repo's cost guardrails: us-east-1 only, no OpenSearch Serverless).
- A pipeline/script to ingest documents into the vector store.
- CORS on the endpoint so a browser page from the GitHub Pages origin can call
  it directly (same pattern as the prediction endpoint).
- Health/readiness check for the new endpoint.

**Out of scope:**
- The chatbot UI/widget and any frontend changes (F4).
- Streaming responses (single JSON response is enough for this feature).
- Charging for access, rate limiting beyond the default Lambda limits.
- Full multi-document management UI (upload/console for editors).
- OpenSearch, Pinecone, or any non-S3-Vectors vector store (guardrail).

## 3. User-Facing Behavior
**Before:** No way to ask diabetes-related questions anywhere on the site; the
only interactive element is the risk-prediction form.

**After:** A caller (today: an API client; from F4: the chat widget) posts a
natural-language question and receives a JSON answer about diabetes topics.
The answer reflects the project's indexed documents — e.g., questions about
HbA1c, glucose readings, hypertension, BMI, or how the risk inputs relate to
blood sugar — instead of ungrounded opinion. When the document store contains
nothing relevant to a question, the endpoint clearly says so rather than
making claims from nothing. A second endpoint reports service health. The
prediction endpoint and its users are unaffected: same behavior, same
payload, same availability as today.

## 4. Acceptance Criteria
1. The new backend exposes a question-answering endpoint that accepts a
   natural-language question with reasonable length limits and returns HTTP
   200 with a JSON body containing an answer string and the source(s) it was
   grounded in.
2. Asking a question covered by the indexed documents (e.g., about HbA1c)
   returns an answer whose content is consistent with those documents, and
   the response includes one or more document source references.
3. Asking a question with no relevant content in the document store returns
   an explicit no-answer/insufficient-context response (not a fabricated
   answer) with appropriate success status.
4. Malformed requests (empty question, missing field, over-length question)
   return a 4xx with a clear JSON error message.
5. The new endpoint permits browser calls from the GitHub Pages origin
   (CORS preflight succeeds; a cross-origin POST from the frontend origin
   completes).
6. A health/readiness endpoint returns 200 and identifies the RAG service.
7. Both of the following are true on the question-answering path: embeddings
   are served from the project's vector store, and answer text is produced by
   an AWS Bedrock LLM in us-east-1.
8. The prediction service (endpoint, container, response shape) behaves
   exactly as before this feature — no changes to `/predict` or `/health`.
9. End-to-end request latency stays within a reasonable interactive budget:
   the question endpoint responds within a few seconds in typical cases and
   never exceeds the Lambda/Web Adapter configured timeout (exact budget
   confirmed in plan).
10. At least one pytest test exercises the QA endpoint's happy path and one
    tests the malformed-request path, using a mock for Bedrock/vector calls,
    runnable without AWS credentials.
11. Document ingestion is repeatable: running the ingestion pipeline against
    the document set refreshes/replaces the vector store contents
    deterministically (re-running produces the same index state).
12. AWS resources created by this feature stay within repo guardrails:
    us-east-1 only, S3 Vectors for embeddings, no new always-on paid
    infrastructure beyond the documented alarm budget.

## 5. Non-Goals
- Chat UI/widget, message history UI, typing indicator, etc. (F4 does these).
- Conversation memory / multi-turn context threading.
- Streaming (token-by-token) responses.
- Streaming media; fine-tuning any model.
- Any change to the frozen prediction service (`app/`, `Dockerfile`, model
  artifacts) or `train/diabetes.csv`.
- Authentication/authorization beyond the endpoint access policy chosen in
  the plan (single-user portfolio demo).

## 6. Dependencies
- **F2 (complete):** its policy pages provide the site context this feature's
  content serves, but no technical coupling.
- **AWS (us-east-1):** new Lambda function + Lambda Web Adapter pattern as
  deployed for the service; Amazon Bedrock (embedding + LLM, with model
  access enabled in the account); S3 Vectors (vector bucket + index).
- **The deployed chatbot of F4** will consume this endpoint later; nothing in
  F3 depends on F4.
- **Files/modules this feature will touch:** new backend code in new
  directories only; no frozen files touched. The `app/` service is reused
  only as the deployment-pattern reference, never modified.

## 7. Risks & Unknowns
- **Bedrock model access not granted in this account** for the chosen
  embedding/LLM models — could block development until access requests are
  approved (model choice + enablement is an Open Question and a plan-time
  step).
- **S3 Vectors maturity/limits** (indexes, dimension caps, request rates):
  constrained workload must fit within current quotas; if a hard limit
  blocks, the fallback (still guardrail-compliant) must be agreed before
  code exists.
- **Answer quality** depends on the corpus; placeholder/dummy documents would
  make the demo weak. Document set quality is an Open Question: without
  real source material the demo can be built and validated on an agreed
  sample set.
- **Cost creep:** Bedrock inference + embeddings spend is the first sustained
  API spend outside the already-paid prediction path; the $20 alarm and
  us-east-1 scope contain it. Free-tier embedding/LLM model choices keep the
  demo well under alarm.
- **CORS behavior parity** with `/predict` must be verified from the actual
  frontend origin, not just a test origin.
- **Lambda Web Adapter container size/timeout** limits: RAG request path
  (embed + retrieve + generate) is slower than `/predict`; container or
  timeout configurations may need to be documented if latency is
  significant.

## 8. Open Questions
Must be resolved before plan.md is written; none of them block drafting the
spec itself:
1. **Corpus**: which documents form the knowledge base, and where do they
   live? (Candidates: curated diabetes FAQs/policy pages, content about
   the model's features, or a placeholder sample set until real content
   exists.)
2. **models** (exact selections to be pinned in plan): which Bedrock
   embedding model (e.g., Titan Text Embeddings V2) and which Bedrock LLM
   (e.g., a Claude model) should the pipeline and answer flow use?
3. **Endpoint shape**: is a single `/ask` endpoint the right contract, and
   what are the response fields (answer, sources, confidence/tokens)?
4. **Access policy** for the new Lambda Function URL (same open-access as
   `/predict`'s URL, or AWS-IAM-restricted for the demo)?
5. **Latency budget**: what response-time ceiling do we accept for the
   interactive F4 widget (this drives embedding/k/n settings and timeout
   config)?
6. **IaC/deployment**: is the repo deploying with console/scripts only
   (current pattern) or should this feature introduce AWS SAM/CDK? (Any
   new tooling must still be additive and not touch existing deploy
   scripts.)

## 9. References
- AWS Bedrock: https://docs.aws.amazon.com/bedrock/
- AWS S3 Vectors: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html
- Lambda Web Adapter: https://github.com/awslabs/aws-lambda-web-adapter
- Existing prediction endpoint (the integration/CORS pattern F3 mirrors):
  https://xa22mu3snncho7eo5rxrua6qvm0ckdwu.lambda-url.us-east-1.on.aws
- Repo guardrails (CLAUDE.md): Cost Guardrails section