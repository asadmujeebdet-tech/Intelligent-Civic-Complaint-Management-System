"""Embed the full HTML UI inside Streamlit (identical to http://localhost:8000)."""
import logging
import socket
import threading
import time
import urllib.error
import urllib.request

import streamlit as st

from backend.app.deployment_config import get_backend_api_url, get_iframe_url, is_streamlit_cloud

logger = logging.getLogger("civiclens.shell")

CHROME_HIDE_CSS = """
<style>
    .stApp { background-color: #F8FAFC; }
    header[data-testid="stHeader"] { display: none; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    footer { visibility: hidden; height: 0; }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    [data-testid="stAppViewContainer"] > section {
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stAppViewContainer"] {
        padding: 0 !important;
    }
    /* Full-height iframe on desktop + mobile */
    [data-testid="stIframe"] {
        width: 100% !important;
    }
    [data-testid="stIframe"] iframe,
    iframe[title="CivicLens AI"] {
        width: 100% !important;
        min-height: 100vh !important;
        height: 100vh !important;
        border: none !important;
        display: block !important;
    }
</style>
"""


def _url_healthy(base: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base.rstrip('/')}/health", timeout=10) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        logger.warning("Health check failed for %s: %s", base, exc)
        return False


def _ensure_local_server() -> bool:
    from backend.app.deployment_config import get_local_dev_url

    local_base = get_local_dev_url()
    host = "0.0.0.0"
    port = int(local_base.split(":")[-1])

    if _url_healthy(local_base):
        return True

    if is_streamlit_cloud():
        return False

    import uvicorn

    key = "local_api_started"
    if not st.session_state.get(key):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            port_busy = sock.connect_ex(("127.0.0.1", port)) == 0
        if not port_busy:
            st.session_state[key] = True
            threading.Thread(
                target=lambda: uvicorn.run(
                    "backend.app.main:app",
                    host=host,
                    port=port,
                    log_level="warning",
                    access_log=False,
                ),
                daemon=True,
            ).start()
        else:
            st.session_state[key] = True

    for _ in range(50):
        if _url_healthy(local_base):
            return True
        time.sleep(0.4)
    return _url_healthy(local_base)


def render_civiclens_app(path: str = "/") -> None:
    st.set_page_config(
        page_title="CivicLens AI",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CHROME_HIDE_CSS, unsafe_allow_html=True)

    url = get_iframe_url(path)
    if not url:
        st.error("Could not resolve application URL.")
        return

    backend = get_backend_api_url()
    if backend:
        if not _url_healthy(backend):
            with st.spinner("Connecting…"):
                for _ in range(25):
                    if _url_healthy(backend):
                        break
                    time.sleep(2)
    else:
        with st.spinner("Loading CivicLens AI…"):
            if not _ensure_local_server():
                st.error("Service temporarily unavailable.")
                st.info(
                    "Start the server in another terminal:\n\n"
                    "`python run_server.py`\n\n"
                    "Then refresh this page."
                )
                return

    logger.info("Embedding HTML UI: %s", url)

    try:
        # Full-viewport iframe — matches direct http://localhost:8000 experience
        if hasattr(st, "html"):
            st.html(
                f'<iframe src="{url}" title="CivicLens AI" '
                f'style="width:100%;height:100vh;border:none;display:block;" '
                f'allow="clipboard-write" loading="eager"></iframe>',
                unsafe_allow_javascript=False,
            )
        else:
            st.iframe(url, height=900, width="stretch")
    except Exception as exc:
        logger.exception("Iframe render failed: %s", exc)
        try:
            st.iframe(url, height=900, width="stretch")
        except Exception:
            st.error("Service temporarily unavailable.")
