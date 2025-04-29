import shelve
import time
import logging
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
dashscope_api_key= os.getenv("DASHSCOPE_API_KEY")

client = OpenAI(api_key=dashscope_api_key, base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1")





def check_if_chat_exists(wa_id,name):
    logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
    with shelve.open("chat_history_db") as chat_shelf:
        return chat_shelf.get(wa_id, [])

def store_chat_history(wa_id, chat_history):
    with shelve.open("chat_history_db", writeback=True) as chat_shelf:
        chat_shelf[wa_id] = chat_history

def generate_response(message_body, wa_id, name):
    # Retrieve existing chat history
    chat_history = check_if_chat_exists(wa_id,name)
    
    # Append the new user message
    chat_history.append({"role": "user", "content": message_body})
    
    response = client.chat.completions.create(
                model="qwen-plus",
                messages=chat_history,
                max_tokens=100  # Adjust as needed
            )
    
    # Extract and log the response
    new_message = response.choices[0].message.content
    logging.info(f"Generated message: {new_message}")
    
    # Append assistant response to history
    chat_history.append({"role": "assistant", "content": new_message})
    
    # Store updated chat history
    store_chat_history(wa_id, chat_history)
    
    return new_message



