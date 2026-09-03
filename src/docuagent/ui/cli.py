"""CLI launcher for Streamlit application."""

import sys
from pathlib import Path
from streamlit.web import cli as stcli


def run_ui():
    """Launch Streamlit with docuagent.ui.app."""
    app_path = str(Path(__file__).resolve().parent / "app.py")
    sys.argv = ["streamlit", "run", app_path]
    sys.exit(stcli.main())


if __name__ == "__main__":
    run_ui()
