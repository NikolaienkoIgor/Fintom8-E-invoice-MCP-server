"""
App Engine / HTTP entrypoint: expose the ASGI app so uvicorn can serve it.
Adds src/ to the path so fintom8_mcp is importable when deps are installed via requirements.txt.
"""
import sys
from pathlib import Path

# Ensure src/ is on path (App Engine only installs from requirements.txt, not the package)
_root = Path(__file__).resolve().parent
_src = _root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from fintom8_mcp.server import app  # noqa: E402

__all__ = ["app"]
