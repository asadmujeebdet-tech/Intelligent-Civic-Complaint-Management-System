"""
Streamlit wrapper — shows ONLY the Bootstrap HTML UI (zero Streamlit sidebar/nav).
Identical to opening http://localhost:8000 after python run_server.py
"""
import logging
import socket
import threading
import time
import urllib.error
import urllib.request

import streamlit as st

from backend.app.deployment_config import get_backend_api_url, get_iframe_url, is_streamlit_cloud

logger = logging.getLogger("civiclens.shell")

# Hide ALL Streamlit chrome — no left nav, no header, no footer
HIDE_STREAMLIT_CSS = """
<style>
    #MainMenu, header, footer, [data-testid="stHeader"],
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stSidebar"], [data-testid="stSidebarNav"],
    [data-testid="collapsedControl"], section[data-testid="stSidebar"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
    }
    .stApp { background-color: #F8FAFC; }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    [data-testid="stAppViewContainer"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stAppViewContainer"] > section {
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stMainBlockContainer"] {
        padding: 0 !important;
        max-width: 100% !important;
    }
    iframe[title="CivicLens AI"] {
        width: 100vw !important;
        min-height: 100vh !important;
        height: 100vh !important;
        border: none !important;
        display: block !important;
        margin: 0 !important;
        padding: 0 !important;
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


def _start_local_api() -> bool:
    from backend.app.deployment_config import get_local_dev_url

    local_base = get_local_dev_url()
    port = int(local_base.split(":")[-1])

    if _url_healthy(local_base):
        return True

    import uvicorn

    key = "api_thread_started"
    if not st.session_state.get(key):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            port_free = sock.connect_ex(("127.0.0.1", port)) != 0
        if port_free:
            st.session_state[key] = True
            threading.Thread(
                target=lambda: uvicorn.run(
                    "backend.app.main:app",
                    host="0.0.0.0",
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
    st.markdown(HIDE_STREAMLIT_CSS, unsafe_allow_html=True)

    url = get_iframe_url(path)
    backend = get_backend_api_url()

    # Streamlit Cloud without a public backend URL cannot embed localhost HTML
    if is_streamlit_cloud() and not url:
        st.error("HTML UI requires a public backend URL on Streamlit Cloud.")
        st.markdown(
            """
            For the **same UI as `python run_server.py`** locally, run:

            ```bash
            python run_server.py
            ```
            Then open **http://localhost:8000**

            For cloud deploy, add a public `BACKEND_API_URL` in Secrets, or use local hosting.
            """
        )
        return

    if backend:
        if not _url_healthy(backend):
            with st.spinner("Connecting…"):
                for _ in range(25):
                    if _url_healthy(backend):
                        break
                    time.sleep(2)
        if not _url_healthy(backend):
            st.error("Service temporarily unavailable.")
            return
    else:
        with st.spinner("Loading CivicLens AI…"):
            if not _start_local_api():
                st.error("Service temporarily unavailable.")
                st.code("python run_server.py", language="bash")
                st.caption("Run the command above in a terminal, then refresh.")
                return

    logger.info("HTML UI iframe: %s", url)

    try:
        st.html(
            f'<iframe src="{url}" title="CivicLens AI" '
            f'style="width:100%;height:100vh;border:none;" allow="clipboard-write"></iframe>',
            unsafe_allow_javascript=False,
        )
    except Exception as exc:
        logger.exception("Iframe failed: %s", exc)
        st.error("Service temporarily unavailable.")
