"""
Streamlit shell — shows the same HTML UI as `python run_server.py`.

Local:      auto-starts or reuses http://127.0.0.1:8000
Cloud:      iframes APP_URL (full app deployed on Render — same UI + API)
"""
import os
import socket
import threading
import time
import urllib.error
import urllib.request

import streamlit as st

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
LOCAL_BASE = f"http://{API_HOST}:{API_PORT}"

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
    iframe { min-height: 92vh !important; }
</style>
"""


def _get_secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


def _deployed_app_url() -> str:
    """Public URL where run_server / run_api is hosted (e.g. Render)."""
    return (
        _get_secret("APP_URL")
        or os.getenv("APP_URL", "").strip()
        or _get_secret("FRONTEND_URL")
        or os.getenv("FRONTEND_URL", "").strip()
    ).rstrip("/")


def _is_streamlit_cloud() -> bool:
    return bool(
        os.getenv("STREAMLIT_SHARING")
        or os.getenv("STREAMLIT_SHARING_MODE")
        or ".streamlit.app" in os.getenv("HOSTNAME", "")
    )


def _url_healthy(base: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base.rstrip('/')}/health", timeout=10) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _port_open(port: int, host: str = API_HOST) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def _run_local_server() -> None:
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=API_HOST,
        port=API_PORT,
        log_level="warning",
        access_log=False,
    )


def _ensure_local_server(max_wait: float = 45.0) -> bool:
    key = f"local_api_{API_HOST}_{API_PORT}"
    start_key = f"local_start_{API_HOST}_{API_PORT}"

    if st.session_state.get(key) and _url_healthy(LOCAL_BASE):
        return True
    if _url_healthy(LOCAL_BASE):
        st.session_state[key] = True
        return True

    if _port_open(API_PORT):
        deadline = time.time() + max_wait
        while time.time() < deadline:
            if _url_healthy(LOCAL_BASE):
                st.session_state[key] = True
                return True
            time.sleep(0.4)
        return False

    if not st.session_state.get(start_key):
        st.session_state[start_key] = True
        threading.Thread(target=_run_local_server, daemon=True).start()

    deadline = time.time() + max_wait
    while time.time() < deadline:
        if _url_healthy(LOCAL_BASE):
            st.session_state[key] = True
            return True
        time.sleep(0.4)
    return False


def render_civiclens_app(path: str = "/") -> None:
    """Full-screen iframe of the Bootstrap HTML UI (identical to run_server.py)."""
    st.set_page_config(
        page_title="CivicLens AI",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CHROME_HIDE_CSS, unsafe_allow_html=True)

    deployed = _deployed_app_url()

    if deployed:
        url = f"{deployed}{path}"
        if not _url_healthy(deployed):
            st.warning(f"Waiting for app at `{deployed}` (Render free tier may take ~60s to wake up)…")
            with st.spinner("Connecting…"):
                for _ in range(30):
                    if _url_healthy(deployed):
                        break
                    time.sleep(2)
        if not _url_healthy(deployed):
            st.error(f"Cannot reach `{deployed}/health`. Check Render deploy and secrets.")
            st.info("Deploy with `render.yaml`, then set `APP_URL` in Streamlit secrets to your Render URL.")
            return
    else:
        if _is_streamlit_cloud():
            st.error("**APP_URL** is required on Streamlit Cloud.")
            st.markdown(
                """
                Streamlit Cloud cannot run the HTML server itself. Deploy the **full app** on Render
                (same UI as `python run_server.py`), then add this secret:

                ```toml
                APP_URL = "https://your-app.onrender.com"
                ```
                """
            )
            st.caption("Full setup guide: **STREAMLIT_CLOUD.md** in the project repo.")
            return
        with st.spinner("Starting CivicLens AI…"):
            if not _ensure_local_server():
                st.error("Could not start local server. Run `python run_server.py` in another terminal.")
                return
        url = f"{LOCAL_BASE}{path}"

    st.iframe(url, height=1000, width="stretch")
