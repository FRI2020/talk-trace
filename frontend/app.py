import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils.headers import (
    fetch_contacts,
    fetch_conversation,
    toggle_human_chat,
    send_user_message,
)

POLLING_INTERVAL = 5000  # milliseconds

def main():
    st.sidebar.title("👋 TalkTracer App")

    # 1) Auto-refresh every POLLING_INTERVAL ms
    #    This reruns the script automatically.
    st_autorefresh(interval=POLLING_INTERVAL, key="chat_refresh")

    # 2) Choose your contact and human-chat toggle
    wa_id = st.sidebar.selectbox("Choose your customer:", fetch_contacts())
    human_access = st.sidebar.checkbox("Activate Human Chat", False)

    # 3) Push toggle immediately on change
    toggle_human_chat(wa_id, human_access)

    # 4) Fetch *fresh* conversation for this wa_id
    conversation = fetch_conversation(wa_id) or []

    # 5) Render every message straight from the backend
    for msg in conversation:
        role = "user" if msg["SENDER"] == wa_id else "assistant"
        with st.chat_message(role):
            st.markdown(msg["MESSAGE"])

    # 6) If human chat is on, show input box
    if human_access:
        user_input = st.chat_input("Type your message here…")
        if user_input:
            success = send_user_message(wa_id, user_input)
            if not success:
                st.error("Failed to send message")
            # no need to manually rerun — autorefresh will pick it up

if __name__ == "__main__":
    main()
