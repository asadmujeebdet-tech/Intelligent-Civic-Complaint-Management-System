"""
CivicLens AI — main entry point

  streamlit run run_server.py   → same HTML UI as python run_server.py (no Streamlit sidebar)
  python run_server.py          → http://localhost:8000
"""
import logging
import sys

logging.basicConfig(level=logging.INFO)

if "streamlit" in sys.modules:
    from streamlit_ui.shell import render_civiclens_app

    render_civiclens_app("/")

elif __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
