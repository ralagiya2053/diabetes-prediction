"""RAG service endpoints: POST /ask, GET /health.

CORS: restricted strictly to the GitHub Pages frontend origin
(env-overridable), applied at the app level — the Function URL CORS
setting must stay DISABLED to avoid duplicate preflight headers
(plan Section 4 decision).
"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import generation
import retrieval
from schema import AskRequest, AskResponse

FRONTEND_ORIGIN = os.environ.get(
    "FRONTEND_ORIGIN", "https://ralagiya2053.github.io"
)

app = FastAPI(title="Diabetes RAG API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,
)

# Question -> answer flow. Patchable module functions (tests replace them).
_retrieve = retrieval.query_chunks
_generate = generation.generate_answer


@app.get("/health")
def health():
    return {"status": "ok", "service": "rag"}


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    try:
        chunks = _retrieve(payload.question)
    except Exception as err:  # retrieval/infra failure -> 5xx JSON, not a crash page
        raise HTTPException(status_code=500, detail=f"retrieval failed: {err}")

    if not chunks:
        return AskResponse(
            answer=generation.INSUFFICIENT_CONTEXT_ANSWER,
            sources=[],
        )

    answer = _generate(payload.question, chunks)
    sources = list(dict.fromkeys(c["source"] for c in chunks))
    return AskResponse(answer=answer, sources=sources)


# Keep validation failures as small JSON bodies (still 422 by default, but
# normalized so a client always gets {"detail": ...}).
@app.exception_handler(RequestValidationError)
async def validation_handler(_request, exc: RequestValidationError):
    first = exc.errors()[0]["msg"] if exc.errors() else "invalid request"
    return JSONResponse(status_code=422, content={"detail": f"invalid question: {first}"})