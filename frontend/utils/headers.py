
import requests
import streamlit as st

API_URL_HISTORY = "http://backend:8080/history"
API_URL_SENDING = "http://backend:8080/sending"
API_URL_HUMAN = "http://backend:8080/toggle-human-chat" 
API_CONTACTS_URL = "http://backend:8080/contacts" 


def fetch_contacts():
    try:
        response = requests.get(API_CONTACTS_URL)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.json().get('detail')}")
    except Exception as e:
        st.error(f"Request failed: {e}")
    return []







def fetch_conversation(wa_id):
    try:
        response = requests.post(f"{API_URL_HISTORY}?user_id={wa_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.json().get('detail')}")
    except Exception as e:
        st.error(f"Request failed: {e}")
    return []

def toggle_human_chat(wa_id, activate):
    payload = {"wa_id": wa_id, "activate": activate}
    try:
        response = requests.post(API_URL_HUMAN, json=payload)
        if response.status_code == 200:
            return response.json().get("message")
        else:
            st.error(f"❌ Error: {response.text}")
    except Exception as e:
        st.error(f"⚠️ Failed to reach API: {e}")
    return None

def send_user_message(wa_id, message):
    payload = {"wa_id": wa_id, "message": message}
    try:
        response = requests.post(API_URL_SENDING, json=payload)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error sending message: {e}")
    return False
    
       