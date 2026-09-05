import sys
from pathlib import Path

# Ensure 'src' directory is in Python path for Vercel serverless runtime
root_dir = Path(__file__).resolve().parent
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from docuagent.api.app import app

__all__ = ["app"]
