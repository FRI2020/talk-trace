from pydantic import BaseModel
import hashlib
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import logging
import json
import hashlib
import hmac
import os
from fastapi import FastAPI
from fastapi import Header, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from utils.whatsapp_utils import is_valid_whatsapp_message, process_whatsapp_message, send_message_to_admin
from decorators.security import verify_signature
from fastapi import Request
import re
from sqlalchemy.ext.asyncio import AsyncSession
from database.sqlite.database import  get_db_h
from database.sqlite.crud import  ChatHistoCRUD, ContactCRUD
from typing import List
from database.sqlite.schemas import MessageOut, ToggleHumanChatPayload, MessagePayload
from fastapi.middleware.cors import CORSMiddleware 

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables from .env file
load_dotenv()

VERIFY_TOKEN    = os.getenv("VERIFY_TOKEN")
APP_SECRET    = os.getenv("APP_SECRET")





# Webhook verification (GET request)
@app.get("/webhook")
async def verify_webhook(request: Request):
    """Verify webhook when WhatsApp sends a GET request."""
    
    # Extract query parameters manually
    hub_mode = request.query_params.get("hub.mode")
    hub_challenge = request.query_params.get("hub.challenge")
    hub_verify_token = request.query_params.get("hub.verify_token")
    
    if not hub_mode or not hub_challenge or not hub_verify_token:
        raise HTTPException(status_code=400, detail="Missing required query parameters")

    # Perform the verification check
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)  # Respond with the challenge to complete the verification
    else:
        raise HTTPException(status_code=403, detail="Verification failed")


# Handle incoming messages (POST request)
@app.post("/webhook")
async def handle_message(request: Request, _=Depends(verify_signature),  db_h: AsyncSession = Depends(get_db_h)):
    """
    Handle incoming webhook events from the WhatsApp API.
    
    Processes incoming WhatsApp messages and other events such as delivery statuses.
    If the event is a valid message, it gets processed. If the incoming payload is 
    not a recognized WhatsApp event, an error is returned.

    Every message send will trigger multiple HTTP requests to your webhook: message, sent, delivered, read.
    
    Returns:
        JSON response with status and appropriate HTTP status code.
    """
    try:
        body = await request.json()
        logging.info(f"Received body: {body}")

        # Check if it's a WhatsApp status update
        if (
            body.get("entry", [{}])[0]
            .get("changes", [{}])[0]
            .get("value", {})
            .get("statuses")
        ):
            logging.info("Received a WhatsApp status update.")
            return JSONResponse({"status": "ok"}, status_code=200)
        
        
        # Validate and process WhatsApp messages
        if is_valid_whatsapp_message(body):

            message = body["entry"][0]["changes"][0]["value"]["messages"][0]
            SENDER = message["from"]
            RECEIVER =  os.getenv("PHONE_NUMBER_ID")
            
            exists = await ContactCRUD.phone_number_exists(db_h, SENDER)
            if not exists:
                # If the sender's phone number doesn't exist in the database, add it
                new_contact = await ContactCRUD.add_contact(db_h, PHONE_NUMBER=SENDER, AI_ACTIVE=1, STATUS=1)
                if new_contact is None:
                    logging.error("Failed to insert new contact into the database.")
                    return JSONResponse(
                        {"status": "error", "message": "Failed to insert new contact"}, status_code=500
                    )

            result = await ContactCRUD.get_status_and_ai_active(db_h, SENDER)

        
            message = body["entry"][0]["changes"][0]["value"]["messages"][0]
            message_body_type = message["type"]
            if message_body_type == "text":

                MESSAGE= body["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

                insert_message = await ChatHistoCRUD.add_message(db_h, SENDER, RECEIVER, MESSAGE)

            if result['AI_ACTIVE']==1 and result['STATUS']==1:

                MESSAGE,  ANSWER =  process_whatsapp_message(body)
                if message_body_type == "audio":
                    insert_message = await ChatHistoCRUD.add_message(db_h, SENDER, RECEIVER, MESSAGE)

                if insert_message is None:
                        logging.error("Failed to insert new message into the database.")
                        return JSONResponse(
                            {"status": "error", "message": "Failed to insert new message"}, status_code=500
                        )
                else:
                    insert_answer = await ChatHistoCRUD.add_message(db_h, RECEIVER, SENDER, ANSWER)
                    if insert_answer is None:
                        logging.error("Failed to insert the answer into the database.")
                        return JSONResponse(
                            {"status": "error", "message": "Failed to insert the answer into the database."}, status_code=500
                        )
                return JSONResponse({"status": "ok"}, status_code=200)
        else:
            # If it's not a valid WhatsApp API event, return error
            return JSONResponse(
                {"status": "error", "message": "Not a WhatsApp API event"}, status_code=404
            )

    except json.JSONDecodeError:
        logging.error("Failed to decode JSON")
        return JSONResponse(
            {"status": "error", "message": "Invalid JSON provided"}, status_code=400
        )
    


@app.post("/history", response_model=List[MessageOut])
async def get_conversation(user_id: str, db: AsyncSession = Depends(get_db_h)):
    """
    Get full conversation history for a user (by phone or user_id).
    """
    conversation = await ChatHistoCRUD.get_chat_by_user(db, SENDER=user_id, RECEIVER=os.getenv("PHONE_NUMBER_ID"))
    
    if not conversation:
        raise HTTPException(status_code=404, detail="No conversation found for this user.")

    return conversation




@app.post("/sending")
async def send_message_admin(payload: MessagePayload, db_h: AsyncSession = Depends(get_db_h)):
    try:
        SENDER = os.getenv("PHONE_NUMBER_ID")
        RECEIVER =  payload.wa_id
        print(payload.message)
        # Check if wa_id and message are valid
        if not payload.message or not payload.wa_id:
            return {"error": "Missing message or wa_id"}
        
        # Call the function to send the message to the admin (external service like WhatsApp)
        send_message =  send_message_to_admin(payload.message, payload.wa_id)
        if send_message is None:
                    logging.error("Failed to insert new message into the database.")
                    return JSONResponse(
                        {"status": "error", "message": "Failed to insert new message"}, status_code=500
                    )
        else:
            insert_answer = await ChatHistoCRUD.add_message(db_h, SENDER, RECEIVER, payload.message)
            if insert_answer is None:
                logging.error("Failed to insert the answer into the database.")
                return JSONResponse(
                    {"status": "error", "message": "Failed to insert the answer into the database."}, status_code=500
                )
        
        return {"status": "Message sent"}
    except Exception as e:
        return {"error": str(e)}




@app.post("/toggle-human-chat")
async def toggle_human_chat(payload: ToggleHumanChatPayload, db_h: AsyncSession = Depends(get_db_h)):
    try:
        if not payload.wa_id:
            return {"error": "Missing phone number (wa_id)"}

        new_ai_active_value = 0 if payload.activate else 1

        update_result = await ContactCRUD.update_contact(
            db=db_h,
            PHONE_NUMBER=payload.wa_id,
            AI_ACTIVE=new_ai_active_value
        )

        if update_result is None:
            return JSONResponse(
                {"status": "error", "message": "Contact not found or update failed"},
                status_code=404
            )

        return {
            "status": "success",
            "message": "Human chat activated" if payload.activate else "AI reactivated",
            "contact": {
                "PHONE_NUMBER": update_result.PHONE_NUMBER,
                "AI_ACTIVE": update_result.AI_ACTIVE,
                "STATUS": update_result.STATUS,
            }
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/contacts", response_model=list[str])
async def read_contacts( db_h: AsyncSession = Depends(get_db_h)):
    contacts = await ContactCRUD.get_all_contacts(db_h)
    return contacts or []










# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


