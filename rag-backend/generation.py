"""Grounded answer generation with a Bedrock LLM (Claude 3 Haiku).

Config from environment variables:

  LLM_MODEL_ID   Bedrock LLM (default: anthropic.claude-3-haiku-20240307-v1:0)
  AWS_REGION     defaults to us-east-1 (repo guardrail)
"""

import os
from functools import lru_cache

import boto3

DEFAULT_LLM_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

# Shown verbatim when retrieval finds nothing relevant (no LLM call).
INSUFFICIENT_CONTEXT_ANSWER = (
    "I don't have relevant information about that in the indexed documents. "
    "Try asking about the topics covered by the site's documents."
)

SYSTEM_PROMPT = (
    "You answer questions about topics covered by this website's documents. "
    "Ground every claim in the CONTEXT you are given. Do not use outside "
    "knowledge, do not speculate, and never invent facts. If the CONTEXT does "
    "not contain what is needed to answer, reply exactly with: "
    "\"I don't have relevant information about that in the indexed documents.\" "
    "Keep answers short and factual."
)


def _env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@lru_cache(maxsize=1)
def llm_model_id() -> str:
    return _env("LLM_MODEL_ID", DEFAULT_LLM_MODEL_ID)


@lru_cache(maxsize=1)
def _bedrock_runtime():
    return boto3.client("bedrock-runtime", region_name=_env("AWS_REGION", "us-east-1"))


def generate_answer(question: str, chunks: list[dict[str, str]]) -> str:
    """Generate a grounded answer for a question from retrieved chunks.

    Must only be called when `chunks` is non-empty — the endpoint enforces
    the insufficient-context fast path before calling this.
    """
    context = "\n\n---\n\n".join(
        f"[{c['source']}]\n{c['text']}" for c in chunks
    )

    resp = _bedrock_runtime().converse(
        modelId=llm_model_id(),
        system=[{"text": SYSTEM_PROMPT}],
        messages=[
            {
                "role": "user",
                "content": [{"text": f"CONTEXT:\n\n{context}\n\nQUESTION:\n\n{question}"}],
            }
        ],
        inferenceConfig={
            "maxTokens": 512,
            "temperature": 0.0,
        },
    )

    parts = resp.get("output", {}).get("message", {}).get("content", [])
    text = "".join(p.get("text", "") for p in parts).strip()
    if not text:
        text = INSUFFICIENT_CONTEXT_ANSWER
    return text