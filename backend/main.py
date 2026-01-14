"""Convenience wrapper so `uvicorn main:app` works from the `backend` folder.

This simply re-exports the FastAPI app object defined in `app.main`.
"""

from app.main import app  # re-export for uvicorn
