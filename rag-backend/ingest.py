#!/usr/bin/env python
"""Ingest rag-backend/documents/*.md into an S3 Vectors index.

Chunking: split each markdown file on "## " headings (the file's title
before the first heading becomes its own chunk). Each chunk is embedded
with Titan Text Embeddings V2 and upserted with metadata {"source", "text"}.

Idempotency/AC11: keys are deterministic ("{docname}::{chunk_index}"), so
re-running replaces each key's vector in place for the same corpus. If
documents were removed from the corpus, list_vectors can be used manually
to clean stale keys (kept out of the script on purpose — destructive).

Usage (env required):
  VECTOR_BUCKET_NAME=... VECTOR_INDEX_NAME=... .venv/Scripts/python.exe rag-backend/ingest.py
"""

import sys
from pathlib import Path

import boto3

DOCS_DIR = Path(__file__).resolve().parent / "documents"

# Shared with retrieval.py via the same env contract
import os

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
EMBED_MODEL_ID = os.environ.get("EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
VECTOR_BUCKET_NAME = os.environ.get("VECTOR_BUCKET_NAME")
VECTOR_INDEX_NAME = os.environ.get("VECTOR_INDEX_NAME")

MAX_VECTORS_PER_PUT = 10  # S3 Vectors PutVectors batch cap


def chunk_document(path: Path) -> list[str]:
    """Split markdown on '## ' headings; leading title text is chunk 0."""
    text = path.read_text(encoding="utf-8")
    raw = f"## {text}".split("## ")
    return [c.strip() for c in raw if c.strip()]


def main() -> int:
    if not VECTOR_BUCKET_NAME or not VECTOR_INDEX_NAME:
        print("Set VECTOR_BUCKET_NAME and VECTOR_INDEX_NAME in the environment.")
        return 1

    embed = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    vectors = boto3.service_client("s3vectors", region_name=AWS_REGION)

    total = 0
    for doc in sorted(DOCS_DIR.glob("*.md")):
        chunks = chunk_document(doc)
        batch = []
        for i, chunk in enumerate(chunks):
            resp = embed.invoke_model(
                modelId=EMBED_MODEL_ID,
                body={"inputText": chunk},
            )
            batch.append(
                {
                    "key": f"{doc.name}::{i}",
                    "data": {"float32": resp["embedding"]},
                    "metadata": {"source": doc.name, "text": chunk},
                }
            )
            if len(batch) == MAX_VECTORS_PER_PUT:
                vectors.put_vectors(
                    vectorBucketName=VECTOR_BUCKET_NAME,
                    indexName=VECTOR_INDEX_NAME,
                    vectors=batch,
                )
                total += len(batch)
                batch = []

        if batch:
            vectors.put_vectors(
                vectorBucketName=VECTOR_BUCKET_NAME,
                indexName=VECTOR_INDEX_NAME,
                vectors=batch,
            )
            total += len(batch)

        print(f"{doc.name}: {len(chunks)} chunks upserted")

    print(f"Done. Total vectors: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())