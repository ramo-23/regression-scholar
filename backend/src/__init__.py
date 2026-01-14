from __future__ import annotations

import sys
from pathlib import Path
from dotenv import load_dotenv

# When `src` is imported as a package, ensure the backend root is on sys.path
# so internal imports like `from src.retrieval import X` work when running from
# the backend folder. Also load the backend .env for API keys.
backend_root = Path(__file__).resolve().parents[1]
if str(backend_root) not in sys.path:
	sys.path.insert(0, str(backend_root))

try:
	load_dotenv(backend_root / ".env")
except Exception:
	try:
		load_dotenv()
	except Exception:
		pass

__all__ = ["generation", "retrieval", "processing"]
