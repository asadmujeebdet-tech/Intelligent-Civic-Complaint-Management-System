"""
Deployment mode detection.

Local `streamlit run app.py`  → HTML iframe UI (same as run_server.py)
Streamlit Cloud               → native Streamlit pages (no paid backend required)
"""
from __future__ import annotations

import logging
import os
import re

logger = logging.getLogger("civiclens.deployment")

_LOCALHOST_RE = re.compile(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?", re.I)


def _secret(name: str) -> str:
    try:
        import streamlit as st

        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


def get_backend_api_url() -> str:
    for key in ("BACKEND_API_URL", "APP_URL", "API_URL"):
        val = _secret(key) or os.getenv(key, "").strip()
        if val:
            return val.rstrip("/")
    return ""


def is_streamlit_cloud() -> bool:
    if os.getenv("STREAMLIT_RUNTIME_ENV", "").lower() == "cloud":
        return True
    host_blob = " ".join(
        filter(None, [os.getenv("HOSTNAME", ""), os.getenv("STREAMLIT_SERVER_ADDRESS", "")])
    )
    if ".streamlit.app" in host_blob:
        return True
    if os.getenv("STREAMLIT_SHARING") or os.getenv("STREAMLIT_SHARING_MODE"):
        return True
    try:
        import streamlit as st

        headers = getattr(getattr(st, "context", None), "headers", None)
        if headers and ".streamlit.app" in str(headers.get("Host", "")):
            return True
    except Exception:
        pass
    return False


def is_localhost_url(url: str) -> bool:
    return bool(url and _LOCALHOST_RE.match(url))


def get_local_dev_url() -> str:
    host = os.getenv("API_HOST", "127.0.0.1")
    port = os.getenv("API_PORT", "8000")
    return f"http://{host}:{port}"


def should_use_html_iframe() -> bool:
    """
    Local machine → always use the Bootstrap HTML UI via iframe.
    Streamlit Cloud → only iframe if a public BACKEND_API_URL is configured.
    """
    if is_streamlit_cloud():
        backend = get_backend_api_url()
        use = bool(backend) and not is_localhost_url(backend)
        logger.info("Streamlit Cloud mode: iframe=%s backend=%s", use, backend or "(none)")
        return use
    logger.info("Local mode: using HTML iframe UI at %s", get_local_dev_url())
    return True


def get_iframe_url(path: str = "/") -> str | None:
    backend = get_backend_api_url()
    if backend and not (is_streamlit_cloud() and is_localhost_url(backend)):
        return f"{backend.rstrip('/')}{path}"
    if not is_streamlit_cloud():
        return f"{get_local_dev_url()}{path}"
    return None


def get_api_v1_base() -> str:
    backend = get_backend_api_url()
    if backend and not (is_streamlit_cloud() and is_localhost_url(backend)):
        return f"{backend}/api/v1"
    if not is_streamlit_cloud():
        return "/api/v1"
    return ""
