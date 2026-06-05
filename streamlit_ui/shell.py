"""Streamlit shell — embeds the production HTML UI (never localhost on cloud)."""
import logging
import time
import urllib.error
import urllib.request

import streamlit as st

from backend.app.deployment_config import (
    get_backend_api_url,
    is_local_dev,
    is_streamlit_cloud,
    resolve_iframe_url,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("civiclens.streamlit")

CHROME_HIDE_CSS = """
<style>
    .stApp { background-color: #F8FAFC; }
    header[data-testid="stHeader"] { display: none; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    footer { visibility: hidden; height: 0; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    [data-testid="stAppViewContainer"] > section { padding: 0 !important; }
    iframe { min-height: 92vh !important; width: 100% !important; border: none; }
</style>
"""


def _url_healthy(base: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base.rstrip('/')}/health", timeout=12) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        logger.warning("Health check failed for %s: %s", base, exc)
        return False


def _ensure_local_server() -> bool:
    """Start local FastAPI only when LOCAL_DEV=true (never on Streamlit Cloud)."""
    if is_streamlit_cloud():
        logger.error("Refusing to start local server on Streamlit Cloud")
        return False

    import socket
    import threading

    from backend.app.deployment_config import get_local_dev_url

    local_base = get_local_dev_url()
    host = local_base.split("//")[1].split(":")[0]
    port = int(local_base.split(":")[-1])

    def _run():
        import uvicorn

        uvicorn.run(
            "backend.app.main:app",
            host=host,
            port=port,
            log_level="warning",
            access_log=False,
        )

    key = "local_server_started"
    if not st.session_state.get(key):
        if not _url_healthy(local_base):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                if sock.connect_ex((host, port)) != 0:
                    st.session_state[key] = True
                    threading.Thread(target=_run, daemon=True).start()
        else:
            st.session_state[key] = True

    for _ in range(40):
        if _url_healthy(local_base):
            return True
        time.sleep(0.5)
    return _url_healthy(local_base)


def render_civiclens_app(path: str = "/") -> None:
    st.set_page_config(
        page_title="CivicLens AI",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CHROME_HIDE_CSS, unsafe_allow_html=True)

    logger.info(
        "Streamlit render: cloud=%s local_dev=%s backend=%s",
        is_streamlit_cloud(),
        is_local_dev(),
        get_backend_api_url() or "(not set)",
    )

    url, err = resolve_iframe_url(path)

    if err or not url:
        st.error(err or "Application URL is not configured.")
        st.markdown(
            """
            **Streamlit Cloud requires a public backend URL.**

            Add to **Settings → Secrets**:

            ```toml
            BACKEND_API_URL = "https://YOUR-SERVICE.onrender.com"
            ```

            Deploy the full app on Render (`render.yaml`), then paste that URL.
            """
        )
        return

    if is_local_dev() and not get_backend_api_url():
        with st.spinner("Starting local server…"):
            if not _ensure_local_server():
                try:
                    st.error("Service temporarily unavailable.")
                except Exception:
                    pass
                st.error("Run `python run_server.py` or set BACKEND_API_URL.")
                return
    elif get_backend_api_url():
        if not _url_healthy(get_backend_api_url()):
            st.warning("Waiting for backend to wake up (Render free tier may take ~60s)…")
            with st.spinner("Connecting…"):
                for _ in range(25):
                    if _url_healthy(get_backend_api_url()):
                        break
                    time.sleep(2)
        if not _url_healthy(get_backend_api_url()):
            try:
                st.error("Service temporarily unavailable.")
            except Exception:
                pass
            st.error(f"Cannot reach `{get_backend_api_url()}/health`. Check Render deployment.")
            return

    try:
        st.iframe(url, height=1000, width="stretch")
    except Exception as exc:
        logger.exception("Iframe render failed: %s", exc)
        st.error("Service temporarily unavailable.")
