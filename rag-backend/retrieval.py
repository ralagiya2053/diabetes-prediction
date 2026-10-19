"""Question embedding + S3 Vectors retrieval.

Config comes from environment variables so the module is testable without
hardcoded resource names:

  VECTOR_BUCKET_NAME   S3 vector bucket holding the index (required at runtime)
  VECTOR_INDEX_NAME    vector index name inside the bucket (required at runtime)
  EMBED_MODEL_ID       Bedrock embedding model (default: Titan Text Embeddings V2)
  EMBED_DIM            index/vector dimension (Titan V2 default: 1024)
  AWS_REGION           defaults to us-east-1 (repo guardrail)
"""

import os
from functools import lru_cache
from typing import Dict, List

import boto3

DEFAULT_EMBED_MODEL_ID = "amazon.titan-embed-text-v2:0"
DEFAULT_EMBED_DIM = 1024


def _env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@lru_cache(maxsize=1)
def embed_model_id() -> str:
    return _env("EMBED_MODEL_ID", DEFAULT_EMBED_MODEL_ID)


@lru_cache(maxsize=1)
def embed_dim() -> int:
    return int(_env("EMBED_DIM", str(DEFAULT_EMBED_DIM)))


@lru_cache(maxsize=1)
def _bedrock_runtime():
    return boto3.client("bedrock-runtime", region_name=_env("AWS_REGION", "us-east-1"))


@lru_cache(maxsize=1)
def _s3vectors():
    return boto3.client("s3vectors", region_name=_env("AWS_REGION", "us-east-1"))


def embed_question(question: str) -> List[float]:
    """Embed a single question string with Titan Text Embeddings V2."""
    resp = _bedrock_runtime().invoke_model(
        modelId=embed_model_id(),
        body={"inputText": question},
    )
    return resp["embedding"]


def query_chunks(question: str, k: int = 3) -> List[Dict[str, str]]:
    """Embed the question and return up to k retrieved chunks.

    Each chunk is {"text": <chunk text>, "source": <document filename>}.
    Returns [] when the index is empty or nothing matches.
    """
    vector = embed_question(question)

    resp = _s3vectors().query_vectors(
        vectorBucketName=_env("VECTOR_BUCKET_NAME"),
        indexName=_env("VECTOR_INDEX_NAME"),
        queryVector={"float32": vector},
        topK=k,
        returnMetadata=True,
    )

    chunks: List[Dict[str, str]] = []
    for match in resp.get("matches", []):
        meta = match.get("metadata", {})
        text = meta.get("text")
        source = meta.get("source")
        if text and source:
            chunks.append({"text": text, "source": source})
    return chunks