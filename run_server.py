"""
CivicLens AI — main entry point

  streamlit run run_server.py   → HTML UI (Bootstrap, same as localhost:8000)
  python run_server.py          → direct API + HTML at http://localhost:8000
"""
import logging
import sys

logging.basicConfig(level=logging.INFO)

if "streamlit" in sys.modules:
    from backend.app.deployment_config import should_use_html_iframe

    if should_use_html_iframe():
        from streamlit_ui.shell import render_civiclens_app

        render_civiclens_app("/")
    else:
        from streamlit_ui.native_home import render_native_app

        render_native_app()

elif __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
