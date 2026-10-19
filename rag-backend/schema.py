from typing import List

from pydantic import BaseModel, Field, field_validator

# Single-question contract; keep generous but bounded (plan: over-length -> 4xx)
QUESTION_MAX_CHARS = 1000


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=QUESTION_MAX_CHARS,
        description="Natural-language question about the indexed documents",
    )

    @field_validator("question")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("question must contain non-whitespace text")
        return v


class AskResponse(BaseModel):
    answer: str
    sources: List[str]


class ErrorResponse(BaseModel):
    detail: str