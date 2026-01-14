from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class AskRequest(BaseModel):
    question: str


class Source(BaseModel):
    paper_title: Optional[str] = None
    authors: Optional[str] = None
    section: Optional[str] = None
    link: Optional[str] = None


class AskResponse(BaseModel):
    answer: str
    sources: List[Source]


class HealthResponse(BaseModel):
    status: str = "ok"
