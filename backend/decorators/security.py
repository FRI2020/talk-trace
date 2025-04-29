import hashlib
from dotenv import load_dotenv
import os
import logging
import hashlib
import hmac
import os
from fastapi import FastAPI
from fastapi import Header, HTTPException, Request



# Initialize FastAPI app
app = FastAPI()
# Load environment variables from .env file
load_dotenv()

VERIFY_TOKEN    = os.getenv("VERIFY_TOKEN")
APP_SECRET    = os.getenv("APP_SECRET")





def validate_signature(payload: str, signature: str) -> bool:
    expected_signature = hmac.new(
        bytes(APP_SECRET, "latin-1"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

async def verify_signature(request: Request, x_hub_signature_256: str = Header(None)):
    if not x_hub_signature_256 or not x_hub_signature_256.startswith("sha256="):
        logging.info("Missing or malformed signature")
        raise HTTPException(status_code=403, detail="Invalid signature")

    signature = x_hub_signature_256[7:]
    payload = await request.body()

    if not validate_signature(payload.decode("utf-8"), signature):
        logging.info("Signature verification failed!")
        raise HTTPException(status_code=403, detail="Invalid signature")
