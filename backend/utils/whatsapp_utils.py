import logging
import json
import requests
import re
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import os
import sys
import logging
from services.dashscope_service import generate_response
from services.speech_recognition import transcribe_audio, transcribe_audio_ar

load_dotenv()

# Access the API keys
dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERSION = os.getenv("VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
RECIPIENT_WAID = os.getenv("RECIPIENT_WAID")



# Add the utils folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../services')))





SAVE_DIR = "audio_files/"  # Directory to save audio files

def download_audio_save(media_id):
    """Fetch audio URL and save the file locally."""
    url = f"https://graph.facebook.com/{VERSION}/{media_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    # Get the direct download URL
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to get audio URL: {response.text}")
        return None

    download_url = response.json().get("url")
    if not download_url:
        logging.error("No download URL found.")
        return None

    # Download the audio file
    audio_response = requests.get(download_url, headers=headers)
    if audio_response.status_code == 200:
        os.makedirs(SAVE_DIR, exist_ok=True)
        file_path = os.path.join(SAVE_DIR, f"{media_id}.ogg")

        with open(file_path, "wb") as f:
            f.write(audio_response.content)
        
        logging.info(f"Audio saved: {file_path}")
        return file_path
    else:
        logging.error(f"Failed to download audio: {audio_response.text}")
        return None




def download_audio(media_id):
    """Fetch audio URL and return the raw audio content."""
    url = f"https://graph.facebook.com/{VERSION}/{media_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    # Get the direct download URL
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to get audio URL: {response.text}")
        return None

    download_url = response.json().get("url")
    if not download_url:
        logging.error("No download URL found.")
        return None

    # Download the audio file
    audio_response = requests.get(download_url, headers=headers)
    if audio_response.status_code == 200:
        logging.info("Audio downloaded successfully.")
        return audio_response.content  # Return raw audio content as bytes
    else:
        logging.error(f"Failed to download audio: {audio_response.text}")
        return None
    
def fetch_and_transcribe(media_id):
    """Fetch audio and transcribe it without saving to disk."""
    # Download the raw audio content
    audio_data = download_audio(media_id)
    if not audio_data:
        raise ValueError("Failed to download audio.")

    # Transcribe the audio
    transcription = transcribe_audio(audio_data)
    return transcription

def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )



def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return JSONResponse({"status": "error", "message": "Request timed out"}, status_code=408)
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return JSONResponse({"status": "error", "message": "Failed to send message"}, status_code=500)
    else:
        # Process the response as normal
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text



def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )





# In-memory storage to track registration states (Ideally, use a database)
USER_REGISTRATION_STATE = {}

def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
    
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body_type = message["type"]

    return handle_existing_user(message_body_type, message, wa_id, name)


def handle_existing_user(message_body_type, message, wa_id, name):
    """Handles messages from registered users."""
    
    if message_body_type == "text":
        message_body = message["text"]["body"]
        response = generate_response(message_body, wa_id, name)
        response = process_text_for_whatsapp(response)
        send_message(get_text_message_input(wa_id, response))
        return message_body, response

    elif message_body_type == "audio":
        audio_id = message["audio"]["id"]
        mime_type = message["audio"]["mime_type"]
        logging.info(f"Received voice message - ID: {audio_id}, MIME: {mime_type}")
        try:
            text_transcribe = fetch_and_transcribe(audio_id)
            if text_transcribe:
                logging.info(f"The transcription is : {text_transcribe}")
            response = generate_response(text_transcribe, wa_id, name)
            response = process_text_for_whatsapp(response)
            send_message(get_text_message_input(wa_id, response))
            return text_transcribe, response
        except ValueError as e:
            logging.warning(f"Transcription failed: {e}")
            response = "I couldn't understand your audio. Please record it again."
            send_message(get_text_message_input(wa_id, response))
            return e , response


def send_message_to_admin( response, wa_id):
    """Handles messages from registered users."""

    data = get_text_message_input(wa_id, response)
    return  send_message(data)


