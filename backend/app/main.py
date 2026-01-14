from __future__ import annotations

from typing import Any, Dict, List
import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Support running as `uvicorn app.main:app` (from backend) and
# `uvicorn main:app` (from backend/app). Try package-relative imports first
# and fall back to top-level imports.
try:
    from .schemas import AskRequest, AskResponse, HealthResponse  # type: ignore
    from .services.scholar_service import ScholarService, chunks_to_sources  # type: ignore
except Exception:
    from schemas import AskRequest, AskResponse, HealthResponse  # type: ignore
    from services.scholar_service import ScholarService, chunks_to_sources  # type: ignore


app = FastAPI(title="ScholarAI Backend")

# Configure root logging so our module loggers are visible under uvicorn
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s %(message)s")

# CORS: allow Angular dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    # Create the service and start initialization in background so the app
    # can start quickly while heavy model loading happens asynchronously.
    service = ScholarService()
    app.state.scholar_service = service
    # start initialization in background; errors will be logged by the service
    asyncio.create_task(service.initialize())
    logging.getLogger("scholarai").info("ScholarService created; initialization started in background")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@app.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest) -> AskResponse:
    """Return an expert answer and structured, deduplicated sources.

    Requirements:
    - Always return HTTP 200; embed errors in the response body for AI failures.
    - If the AI fails, return a fallback answer and an empty source list.
    """
    service: ScholarService = getattr(app.state, "scholar_service", None)
    fallback_answer = (
        "I'm sorry — the AI failed to generate an answer at this time."
    )

    if service is None:
        # Service not available; return fallback with explanation
        return AskResponse(answer=fallback_answer, sources=[])

    # If the service exists but AI initialization is still in progress,
    # return a friendly message asking the client to retry shortly.
    if getattr(service, "ai", None) is None:
        return AskResponse(answer="Service is starting; please retry in a moment.", sources=[])

    try:
        result = service.generate_expert_answer(payload.question)
        # Expecting (answer: str, chunks: list)
        if not isinstance(result, (list, tuple)) or len(result) < 1:
            return AskResponse(answer=fallback_answer, sources=[])

        answer = result[0]
        chunks = result[1] if len(result) > 1 else []

        sources = chunks_to_sources(chunks)
        return AskResponse(answer=answer or fallback_answer, sources=sources)

    except Exception as exc:
        # Log exception for debugging but still return HTTP 200 with fallback
        logging.getLogger("scholarai").exception("AI generation failed: %s", exc)
        return AskResponse(answer=fallback_answer, sources=[])


@app.get("/debug")
async def debug() -> Dict[str, Any]:
    """Debug endpoint: shows whether the ScholarService and AI are initialized."""
    service: ScholarService = getattr(app.state, "scholar_service", None)
    if service is None:
        return {"initialized": False, "ai": None}
    ai_obj = getattr(service, "ai", None)
    ai_name = type(ai_obj).__name__ if ai_obj is not None else None
    return {"initialized": True, "ai": ai_name}
