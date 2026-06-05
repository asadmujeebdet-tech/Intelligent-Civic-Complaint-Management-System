import logging

import streamlit as st

logger = logging.getLogger("civiclens.db")


@st.cache_resource
def init_database():
    from backend.app.database import Database

    Database.connect()
    return True


def ensure_db() -> bool:
    try:
        init_database()
        return True
    except Exception as exc:
        logger.exception("Database connection failed")
        st.error("Service temporarily unavailable.")
        st.caption(f"Database error: {exc}")
        st.info("Add `MONGO_URI` and `DB_NAME` in Streamlit Cloud → Settings → Secrets.")
        return False
