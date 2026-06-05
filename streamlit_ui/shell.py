"""Embed the CivicLens HTML UI inside Streamlit."""
import os
import socket
import threading
import time
import urllib.error
import urllib.request

import streamlit as st

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_BASE = f"http://{API_HOST}:{API_PORT}"

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
    }
    [data-testid="stAppViewContainer"] > section {
        padding: 0 !important;
    }
    .civiclens-loader {
        text-align: center;
        padding: 4rem 1rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #1E293B;
    }
    .civiclens-loader h2 {
        color: #2563EB;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .civiclens-loader p { color: #64748b; }
</style>
"""


def _frontend_url() -> str:
    """Public HTTPS URL of the deployed frontend (Netlify). Required on Streamlit Cloud."""
    return os.getenv("FRONTEND_URL", "").strip().rstrip("/")


def _is_streamlit_cloud() -> bool:
    return bool(
        os.getenv("STREAMLIT_SHARING")
        or os.getenv("STREAMLIT_SHARING_MODE")
        or ".streamlit.app" in os.getenv("HOSTNAME", "")
    )


def _resolve_app_url(path: str) -> tuple[str, bool]:
    """
    Return (url, needs_local_server).
    Streamlit Cloud must use FRONTEND_URL (Netlify) — localhost iframes fail in the browser.
    """
    frontend = _frontend_url()
    if frontend:
        base = frontend
        return f"{base}{path}", False
    return f"{API_BASE}{path}", True


def _api_healthy(base: str = API_BASE) -> bool:
    try:
        with urllib.request.urlopen(f"{base}/health", timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _port_open(port: int, host: str = API_HOST) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def _run_api_server() -> None:
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=API_HOST,
        port=API_PORT,
        log_level="warning",
        access_log=False,
    )


def ensure_api_server(max_wait_seconds: float = 45.0) -> bool:
    """Reuse an existing local API, or start one if the port is free."""
    ready_key = f"api_ready_{API_HOST}_{API_PORT}"
    start_key = f"api_start_attempted_{API_HOST}_{API_PORT}"

    if st.session_state.get(ready_key) and _api_healthy():
        return True

    if _api_healthy():
        st.session_state[ready_key] = True
        return True

    if _port_open(API_PORT):
        deadline = time.time() + max_wait_seconds
        while time.time() < deadline:
            if _api_healthy():
                st.session_state[ready_key] = True
                return True
            time.sleep(0.4)
        return False

    if not st.session_state.get(start_key):
        st.session_state[start_key] = True
        thread = threading.Thread(target=_run_api_server, daemon=True)
        thread.start()

    deadline = time.time() + max_wait_seconds
    while time.time() < deadline:
        if _api_healthy():
            st.session_state[ready_key] = True
            return True
        time.sleep(0.4)

    return _api_healthy()


def render_civiclens_app(path: str = "/") -> None:
    """Full-viewport iframe to the HTML UI."""
    st.set_page_config(
        page_title="CivicLens AI",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CHROME_HIDE_CSS, unsafe_allow_html=True)

    url, needs_local = _resolve_app_url(path)

    if needs_local:
        with st.spinner("Loading CivicLens AI…"):
            ready = ensure_api_server()
        if not ready:
            port_busy = _port_open(API_PORT)
            st.markdown(
                '<div class="civiclens-loader"><h2>CivicLens AI</h2>'
                "<p>Could not connect to the application server.</p></div>",
                unsafe_allow_html=True,
            )
            if port_busy:
                st.error(
                    f"Port {API_PORT} is in use but `{API_BASE}/health` did not respond. "
                    "Stop the other process, or set `API_PORT` to a free port."
                )
            else:
                st.error(
                    f"API did not respond at {API_BASE}. "
                    "Run `python run_server.py` locally, or set `FRONTEND_URL` for cloud deploy."
                )
            return
    elif _is_streamlit_cloud() and not _frontend_url():
        st.error(
            "Streamlit Cloud requires **FRONTEND_URL** in app secrets "
            "(your Netlify site URL, e.g. `https://civiclens.netlify.app`). "
            "Localhost cannot be embedded from the cloud."
        )
        st.info("Deploy the frontend on Netlify, set `API_URL` there to your Render API, "
                "then add `FRONTEND_URL` here in Streamlit → Settings → Secrets.")
        return

    # st.iframe accepts: src, width, height, tab_index (no scrolling param)
    st.iframe(url, height=900, width="stretch")
