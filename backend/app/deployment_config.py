"""
Deployment mode detection.

Local `python app.py`     → FastAPI serves HTML at http://localhost:8000
`streamlit run app.py`    → HTML iframe via same-origin /backend mount
Streamlit Cloud           → same /backend mount (no external BACKEND_API_URL required)
Optional BACKEND_API_URL  → iframe a separately hosted API (Render/Railway/etc.)
"""
from __future__ import annotations

import logging
import os
import re
import sys

logger = logging.getLogger("civiclens.deployment")

_LOCALHOST_RE = re.compile(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?", re.I)

# Must match Mount prefix in app.py — only set when Streamlit ASGI mounts FastAPI
MOUNT_PREFIX_ENV = "CIVICLENS_MOUNT_PREFIX"
SAME_ORIGIN_MOUNT = "/backend"


def _secret(name: str) -> str:
    # Do not import streamlit here — that would pollute sys.modules and break
    # standalone FastAPI (`python app.py`) URL resolution.
    if "streamlit" not in sys.modules:
        return ""
    try:
        import streamlit as st

        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


def get_mount_prefix() -> str:
    """Non-empty only when Streamlit Starlette App has mounted FastAPI."""
    return os.getenv(MOUNT_PREFIX_ENV, "").rstrip("/")


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
    if "streamlit" in sys.modules:
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


def is_streamlit_runtime() -> bool:
    return "streamlit" in sys.modules


def should_use_same_origin_mount() -> bool:
    """Use /backend only when explicitly enabled by the Streamlit ASGI app."""
    backend = get_backend_api_url()
    if backend and not (is_streamlit_cloud() and is_localhost_url(backend)):
        return False
    return bool(get_mount_prefix())


def should_use_html_iframe() -> bool:
    """Always use the Bootstrap HTML UI via iframe when possible."""
    return True


def get_iframe_url(path: str = "/") -> str | None:
    backend = get_backend_api_url()
    if backend and not (is_streamlit_cloud() and is_localhost_url(backend)):
        return f"{backend.rstrip('/')}{path}"
    mount = get_mount_prefix() or (SAME_ORIGIN_MOUNT if is_streamlit_runtime() else "")
    if mount:
        return f"{mount}{path}"
    if not is_streamlit_cloud():
        return f"{get_local_dev_url()}{path}"
    return f"{SAME_ORIGIN_MOUNT}{path}"


def get_api_v1_base() -> str:
    backend = get_backend_api_url()
    if backend and not (is_streamlit_cloud() and is_localhost_url(backend)):
        return f"{backend}/api/v1"
    mount = get_mount_prefix()
    if mount:
        return f"{mount}/api/v1"
    return "/api/v1"
