import logging

import streamlit as st

from backend.app.services.chatbot_service import ChatbotService
from streamlit_ui.db import ensure_db
from streamlit_ui.theme import apply_theme, page_title

logger = logging.getLogger("civiclens.chatbot")

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")
apply_theme()
page_title("AI Civic Assistant", "fa-robot")
st.caption("Ask about complaints, trends, hotspots, and reports.")

if not ensure_db():
    st.stop()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Hello! Ask me about complaints, trends, hotspots, or reports."}
    ]

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question…"):
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                answer = ChatbotService.chat_with_complaints(prompt)
                st.markdown(answer)
                st.session_state.chat_messages.append({"role": "assistant", "content": answer})
            except Exception as exc:
                logger.exception("Chatbot failed")
                st.error("Service temporarily unavailable.")
                st.caption(str(exc))
