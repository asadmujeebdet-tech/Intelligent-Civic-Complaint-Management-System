import streamlit as st


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
        st.error(f"Database connection failed: {exc}")
        st.info("Add `MONGO_URI` and `DB_NAME` in Streamlit Cloud → Settings → Secrets.")
        return False
