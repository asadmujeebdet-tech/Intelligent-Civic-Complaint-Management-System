"""
Centralized deployment URLs — never hardcode localhost for production.

Streamlit Cloud secrets (any one of these):
  BACKEND_API_URL = "https://your-app.onrender.com"
  APP_URL = "https://your-app.onrender.com"

Local dev only:
  LOCAL_DEV=true  → allows http://127.0.0.1:8000
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
    """Public HTTPS origin of the full app (FastAPI + frontend)."""
    for key in ("BACKEND_API_URL", "APP_URL", "API_URL", "FRONTEND_URL"):
        val = _secret(key) or os.getenv(key, "").strip()
        if val:
            return val.rstrip("/")
    return ""


def is_local_dev() -> bool:
    return os.getenv("LOCAL_DEV", "").lower() in ("1", "true", "yes")


def is_streamlit_cloud() -> bool:
    if os.getenv("STREAMLIT_RUNTIME_ENV", "").lower() == "cloud":
        return True
    host_blob = " ".join(
        filter(
            None,
            [
                os.getenv("HOSTNAME", ""),
                os.getenv("STREAMLIT_SERVER_ADDRESS", ""),
                os.getenv("STREAMLIT_SERVER_PORT", ""),
            ],
        )
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


def get_api_v1_base() -> str:
    """Browser-facing API base, e.g. https://app.onrender.com/api/v1"""
    backend = get_backend_api_url()
    if backend:
        if is_streamlit_cloud() and is_localhost_url(backend):
            logger.error("BACKEND_API_URL is localhost on Streamlit Cloud — rejected")
            return ""
        return f"{backend}/api/v1"
    if is_local_dev() and not is_streamlit_cloud():
        return "/api/v1"
    return ""


def get_local_dev_url() -> str:
    host = os.getenv("API_HOST", "127.0.0.1")
    port = os.getenv("API_PORT", "8000")
    return f"http://{host}:{port}"


def resolve_iframe_url(path: str = "/") -> tuple[str | None, str | None]:
    """
    Returns (iframe_url, error_message).
    Never returns localhost on Streamlit Cloud (fixes mobile 127.0.0.1 refused).
    """
    backend = get_backend_api_url()

    if backend:
        if is_streamlit_cloud() and is_localhost_url(backend):
            msg = (
                "BACKEND_API_URL must be a public HTTPS URL on Streamlit Cloud, "
                "not localhost or 127.0.0.1."
            )
            logger.error(msg)
            return None, msg
        if not backend.startswith("https://") and is_streamlit_cloud():
            logger.warning("BACKEND_API_URL should use HTTPS for mobile browsers: %s", backend)
        url = f"{backend.rstrip('/')}{path}"
        logger.info("Iframe target (production): %s", url)
        return url, None

    if is_streamlit_cloud():
        msg = (
            "BACKEND_API_URL is not set. Add your Render app URL in Streamlit Cloud secrets, "
            "e.g. BACKEND_API_URL = \"https://civiclens-app.onrender.com\""
        )
        logger.error(msg)
        return None, msg

    if is_local_dev():
        local = get_local_dev_url()
        url = f"{local}{path}"
        logger.warning("LOCAL_DEV iframe: %s (works only on this machine)", url)
        return url, None

    msg = (
        "Set BACKEND_API_URL to your deployed app URL, or LOCAL_DEV=true for local Streamlit."
    )
    logger.error(msg)
    return None, msg
