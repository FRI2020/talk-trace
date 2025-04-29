from pydantic import BaseModel
from datetime import datetime





class MessagePayload(BaseModel):
    message: str
    wa_id: str

class MessageOut(BaseModel):
    SENDER: str
    RECEIVER: str
    MESSAGE: str
    TIMESTAMP: datetime

class MessageSend(BaseModel):
    MESSAGE: str


class ToggleHumanChatPayload(BaseModel):
    wa_id: str
    activate: bool