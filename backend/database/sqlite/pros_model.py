from sqlalchemy import Column, String, Float, Text, TIMESTAMP, CheckConstraint, func
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime

Base = declarative_base()



class CHAT_HISTO(Base):
    __tablename__ = "CHAT_HISTO"

    id = Column(Integer, primary_key=True, index=True)
    SENDER = Column(String, index=True)  # e.g., WhatsApp number
    RECEIVER = Column(String)  # "user" or "ai"
    MESSAGE = Column(Text)
    TIMESTAMP = Column(TIMESTAMP, default="CURRENT_TIMESTAMP")


class CONTACT(Base):
    __tablename__ = "CONTACT"

    ID = Column(Integer, primary_key=True, index=True)
    PHONE_NUMBER = Column(String, unique=True, index=True)  # WhatsApp number
    AI_ACTIVE = Column(Integer, default=1)  # 1 = AI, 0 = Human
    STATUS = Column(Integer, default=1)     # 1 = Active, 0 = Inactive
    DC = Column(DateTime, server_default=func.now())  # Date Created
    DM = Column(DateTime, onupdate=func.now(), default=func.now())  # Date Modified
    DD = Column(DateTime, nullable=True)  # Date Deactivated (optional)    