"""Embed the same HTML UI served by run_server.py inside Streamlit."""
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
    """Reuse an existing API on port 8000, or start one if the port is free."""
    ready_key = f"api_ready_{API_HOST}_{API_PORT}"
    start_key = f"api_start_attempted_{API_HOST}_{API_PORT}"

    if st.session_state.get(ready_key) and _api_healthy():
        return True

    if _api_healthy():
        st.session_state[ready_key] = True
        return True

    port_busy = _port_open(API_PORT)

    # Port taken (e.g. run_server.py already running) — never start a second server
    if port_busy:
        deadline = time.time() + max_wait_seconds
        while time.time() < deadline:
            if _api_healthy():
                st.session_state[ready_key] = True
                return True
            time.sleep(0.4)
        return False

    # Port free — start at most one background server per Streamlit session
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
    """Full-viewport iframe to the HTML UI (same as run_server.py)."""
    st.set_page_config(
        page_title="CivicLens AI",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CHROME_HIDE_CSS, unsafe_allow_html=True)

    with st.spinner("Loading CivicLens AI…"):
        ready = ensure_api_server()

    if not ready:
        port_busy = _port_open(API_PORT)
        st.markdown(
            """
            <div class="civiclens-loader">
                <h2>CivicLens AI</h2>
                <p>Could not connect to the application server.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if port_busy:
            st.error(
                f"Port {API_PORT} is in use but `{API_BASE}/health` did not respond. "
                "Stop the other process on that port, or set `API_PORT` to a free port."
            )
        else:
            st.error(
                f"API did not respond at {API_BASE}. "
                "Check MongoDB credentials in `.env`, or run `python run_server.py` first."
            )
        return

    url = f"{API_BASE}{path}"
    st.iframe(url, height=900, scrolling=False)
