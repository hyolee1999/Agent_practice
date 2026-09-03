"""FastAPI entry point shim.

Delegates directly to the modularized docuagent.api.app package.
"""

from docuagent.api.app import app, run_server

__all__ = ["app", "run_server"]

if __name__ == "__main__":
    run_server()
