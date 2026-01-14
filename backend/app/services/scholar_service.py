from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import sys
import logging
import os

from dotenv import load_dotenv


class MockScholarAI:
    def generate_expert_answer(self, question: str) -> Tuple[str, List[Dict[str, str]]]:
        answer = f"Mock expert answer for: {question}"
        chunks = [
            {
                "paper_title": "A Mock Paper on the Topic",
                "authors": "Doe, J.",
                "section": "Overview",
                "link": "https://example.org/mock-paper",
            }
        ]
        return answer, chunks


def _import_scholarai() -> Optional[Any]:
    """Attempt to import a real ScholarAI implementation from common locations.

    When running `uvicorn main:app` from the `app` folder, the repo root may
    not be on `sys.path`, so we add the backend root to allow `src.generation`
    imports to work.
    """
    # Backend root is two levels up from this file: backend/
    backend_root = Path(__file__).resolve().parents[2]
    # Ensure backend root is on sys.path so `src.generation` can be imported
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))
        logging.getLogger("scholarai.import").debug("Inserted backend root to sys.path: %s", backend_root)

    # Load .env from backend root to ensure GEMINI_API_KEY and other vars are available
    try:
        load_dotenv(backend_root / ".env")
    except Exception:
        pass

    logger = logging.getLogger("scholarai.import")

    # Log whether GEMINI_API_KEY is visible at import time
    try:
        key_present = bool(os.getenv("GEMINI_API_KEY"))
        logger.debug("GEMINI_API_KEY present=%s", key_present)
    except Exception:
        logger.debug("Could not read GEMINI_API_KEY from environment")

    try:
        from src.generation import ScholarAI  # type: ignore

        return ScholarAI
    except Exception as exc:
        logger.debug("Import src.generation failed: %s", exc)
        try:
            from generation import ScholarAI  # type: ignore

            return ScholarAI
        except Exception as exc2:
            logger.debug("Import generation failed: %s", exc2)
            return None


class ScholarService:
    """Wrapper around `ScholarAI` that is initialized once at startup.

    If a real `ScholarAI` cannot be imported, this service falls back to a
    `MockScholarAI` so the app remains functional during development.
    """

    def __init__(self) -> None:
        self.ai: Optional[Any] = None

    async def initialize(self) -> None:
        logger = logging.getLogger("scholarai.init")

        # Re-check GEMINI key visibility at startup
        try:
            key = os.getenv("GEMINI_API_KEY")
            logger.info("GEMINI_API_KEY present=%s", bool(key))
        except Exception:
            logger.info("GEMINI_API_KEY presence unknown")

        Real = _import_scholarai()
        if Real is None:
            logger.info("Real ScholarAI not importable; using MockScholarAI")
            self.ai = MockScholarAI()
        else:
            try:
                logger.info("Initializing real ScholarAI: %s", Real)
                self.ai = Real()
                logger.info("Real ScholarAI initialized successfully: %s", type(self.ai).__name__)
            except Exception as exc:
                logger.exception("Failed to initialize real ScholarAI: %s", exc)
                logger.info("Falling back to MockScholarAI")
                self.ai = MockScholarAI()

    def generate_expert_answer(self, question: str) -> Tuple[str, List[Dict[str, Any]]]:
        if not self.ai:
            raise RuntimeError("AI not initialized")
        return self.ai.generate_expert_answer(question)


def chunks_to_sources(chunks: Optional[List[Any]]) -> List[Dict[str, Optional[str]]]:
    """Convert heterogeneous chunk objects into clean, deduplicated sources.

    Best-effort parsing: handle dicts with common keys, normalize authors list,
    and deduplicate by `link` or by `(paper_title, section)` tuple.
    """
    if not chunks:
        return []

    seen = set()
    sources: List[Dict[str, Optional[str]]] = []

    for chunk in chunks:
        if isinstance(chunk, dict):
            # Prefer metadata nested structure used by the retrieval pipeline
            meta = chunk.get("metadata") or chunk.get("meta") or {}

            title = (
                chunk.get("paper_title")
                or chunk.get("title")
                or chunk.get("paper")
                or meta.get("paper_title")
                or meta.get("title")
            )

            authors = (
                chunk.get("authors")
                or chunk.get("author")
                or meta.get("authors")
                or meta.get("author")
            )
            if isinstance(authors, (list, tuple)):
                authors = ", ".join(str(a) for a in authors)

            section = (
                chunk.get("section")
                or meta.get("section")
                or chunk.get("chunk")
                or chunk.get("context")
                or chunk.get("excerpt")
                or meta.get("section")
                or meta.get("part")
            )

            # Build a link from common metadata keys (paper_id -> arXiv)
            link = (
                chunk.get("link")
                or chunk.get("url")
                or chunk.get("source")
                or meta.get("link")
                or meta.get("url")
                or meta.get("source")
            )
            if not link:
                paper_id = meta.get("paper_id") or meta.get("id")
                if paper_id:
                    # arXiv ids may contain version suffixes like '1234.5678v2'
                    try:
                        arxiv_id = str(paper_id).split("v")[0]
                        link = f"https://arxiv.org/abs/{arxiv_id}"
                    except Exception:
                        link = str(paper_id)
        else:
            # Unknown format: skip non-dict chunks
            continue

        key = link if link else (title, section)
        try:
            if key in seen:
                continue
        except TypeError:
            # Unhashable; coerce to string fallback
            key = str(key)
            if key in seen:
                continue

        seen.add(key)
        sources.append(
            {
                "paper_title": title,
                "authors": authors,
                "section": section,
                "link": link,
            }
        )

    return sources
