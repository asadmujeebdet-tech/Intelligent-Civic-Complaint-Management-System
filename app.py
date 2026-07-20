"""
CivicLens AI — main entry point

  streamlit run app.py   → same Bootstrap HTML UI (FastAPI mounted at /backend)
  python app.py          → http://localhost:8000
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("civiclens")

# Same-origin path where FastAPI (HTML + API) is mounted under Streamlit.
CIVICLENS_MOUNT_PREFIX = "/backend"

_ENTRY = "streamlit_ui/entry.py"


def _sync_streamlit_secrets() -> None:
    """Copy Streamlit Cloud secrets into env + settings for FastAPI."""
    try:
        import streamlit as st

        from backend.app.config import settings

        keys = (
            "MONGO_URI",
            "DB_NAME",
            "GEMINI_API_KEY",
            "GOOGLE_MAP_API_KEY",
            "GOOGLE_MAPS_API_KEY",
            "BACKEND_API_URL",
            "APP_URL",
            "API_URL",
        )
        for key in keys:
            try:
                val = str(st.secrets.get(key, "")).strip()
            except Exception:
                val = ""
            if not val:
                continue
            os.environ[key] = val
            attr = "GOOGLE_MAP_API_KEY" if key == "GOOGLE_MAPS_API_KEY" else key
            if hasattr(settings, attr):
                setattr(
                    settings,
                    attr,
                    val.rstrip("/") if attr == "BACKEND_API_URL" else val,
                )
    except Exception as exc:
        logger.debug("Secret sync skipped: %s", exc)


@asynccontextmanager
async def _asgi_lifespan(_app):
    """Mounted FastAPI startup hooks do not run — connect DB here."""
    _sync_streamlit_secrets()
    from backend.app.database import Database

    Database.connect()
    try:
        yield {}
    finally:
        Database.disconnect()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("PORT") is None,
        log_level="info",
    )
else:
    # ASGI app for `streamlit run` / Streamlit Cloud (must be named `app`).
    os.environ["CIVICLENS_MOUNT_PREFIX"] = CIVICLENS_MOUNT_PREFIX

    from starlette.routing import Mount
    from streamlit.starlette import App

    from backend.app.main import app as _fastapi_app

    app = App(
        _ENTRY,
        routes=[Mount(CIVICLENS_MOUNT_PREFIX, app=_fastapi_app)],
        lifespan=_asgi_lifespan,
    )
