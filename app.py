"""
CivicLens AI

Streamlit Cloud:  streamlit run app.py   (requires BACKEND_API_URL secret)
Local HTML+API:    python run_server.py
Local Streamlit:  LOCAL_DEV=true streamlit run app.py
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
