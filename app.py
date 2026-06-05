"""
CivicLens AI — main entry point

Run Streamlit (same UI as run_server):  streamlit run app.py
Run API + HTML UI directly:             python run_server.py
"""
import sys

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
