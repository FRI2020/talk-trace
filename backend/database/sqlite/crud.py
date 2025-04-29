from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import distinct, update
from database.sqlite.pros_model import  CHAT_HISTO, CONTACT
from sqlalchemy.exc import SQLAlchemyError 
from datetime import datetime
import os

        
class ContactCRUD:
    @staticmethod
    async def add_contact(db: AsyncSession, PHONE_NUMBER: str, AI_ACTIVE: int = 1, STATUS: int = 1):
        """Add a new contact to the DB if it doesn't already exist"""
        try:
            # Check if the phone number already exists
            exists = await ContactCRUD.phone_number_exists(db, PHONE_NUMBER)
            if exists:
                print(f"Contact with phone number {PHONE_NUMBER} already exists.")
                return None  # Return None if the contact already exists

            # If phone number doesn't exist, create the new contact
            current_timestamp = datetime.now()
            new_contact = CONTACT(
                PHONE_NUMBER=PHONE_NUMBER,
                AI_ACTIVE=AI_ACTIVE,
                STATUS=STATUS,
                DC=current_timestamp,
                DM=current_timestamp
            )
            db.add(new_contact)
            await db.commit()
            await db.refresh(new_contact)
            return new_contact

        except SQLAlchemyError as e:
            print(f"An error occurred while saving contact: {e}")
            return None
    
    @staticmethod
    async def update_contact(db: AsyncSession, PHONE_NUMBER: str, AI_ACTIVE: int = None, STATUS: int = None):
        """Update an existing contact's AI_ACTIVE, STATUS or other fields."""
        current_timestamp = datetime.now()
        try:
            update_values = {"DM": current_timestamp}  # Always update DM timestamp
            
            if AI_ACTIVE is not None:
                update_values["AI_ACTIVE"] = AI_ACTIVE
            if STATUS is not None:
                update_values["STATUS"] = STATUS

            stmt = (
                update(CONTACT)
                .where(CONTACT.PHONE_NUMBER == PHONE_NUMBER)
                .values(update_values)
                .execution_options(synchronize_session="fetch")
            )
            result = await db.execute(stmt)
            await db.commit()
            
            if result.rowcount == 0:
                print(f"No contact found with phone number {PHONE_NUMBER}")
                return None
            else:
                # Return the updated contact
                updated_contact = await db.execute(
                    select(CONTACT).filter_by(PHONE_NUMBER=PHONE_NUMBER)
                )
                return updated_contact.scalar_one_or_none()
        except SQLAlchemyError as e:
            print(f"An error occurred while updating contact: {e}")
            return None
    @staticmethod
    async def get_all_contacts(db: AsyncSession):
        """Retrieve all phone numbers from the DB"""
        try:
            result = await db.execute(select(CONTACT.PHONE_NUMBER))
            return result.scalars().all()
        except SQLAlchemyError as e:
            print(f"An error occurred while retrieving contacts: {e}")
            return None
    @staticmethod
    async def phone_number_exists(db: AsyncSession, phone_number: str):
        """Check if a phone number exists in the DB"""
        try:
            result = await db.execute(select(CONTACT).filter_by(PHONE_NUMBER=phone_number))
            contact = result.scalar_one_or_none()
            return contact is not None
        except SQLAlchemyError as e:
            print(f"An error occurred while checking if phone number exists: {e}")
            return False
    @staticmethod
    async def get_status_and_ai_active(db: AsyncSession, PHONE_NUMBER: str):
        """Get the STATUS and AI_ACTIVE values for a given phone number."""
        try:
            result = await db.execute(
                select(CONTACT.STATUS, CONTACT.AI_ACTIVE).filter(CONTACT.PHONE_NUMBER == PHONE_NUMBER)
            )
            contact = result.one_or_none()  # returns a tuple (STATUS, AI_ACTIVE) or None

            if contact:
                return {"STATUS": contact[0], "AI_ACTIVE": contact[1]}
            else:
                return {"error": "Contact not found"}

        except Exception as e:
            print(f"Error fetching contact status/ai_active: {e}")
            return {"error": "Database error"}

        except SQLAlchemyError as e:
            print(f"An error occurred while fetching contact data: {e}")
            return {"error": "Failed to fetch contact data"}  

class ChatHistoCRUD:
    @staticmethod
    async def add_message(db: AsyncSession, SENDER: str, RECEIVER: str, MESSAGE: str):
        """Add a conversation message to the DB"""
        current_timestamp = datetime.now()
        try:
            new_msg = CHAT_HISTO(
                SENDER=SENDER,
                RECEIVER=RECEIVER,
                MESSAGE=MESSAGE,
                TIMESTAMP=current_timestamp
            )
            db.add(new_msg)
            await db.commit()
            await db.refresh(new_msg)
            return new_msg
        except SQLAlchemyError as e:
            print(f"An error occurred while saving conversation: {e}")
            return None

    @staticmethod
    async def get_chat_by_user(db: AsyncSession, SENDER: str, RECEIVER: str):
        """Get all messages by user ID"""
        try:
            result = await db.execute(
                select(CHAT_HISTO).where(
                    ((CHAT_HISTO.SENDER == SENDER) & (CHAT_HISTO.RECEIVER == RECEIVER))
                    | ((CHAT_HISTO.SENDER == RECEIVER) & (CHAT_HISTO.RECEIVER == SENDER)) 
                ).order_by(CHAT_HISTO.TIMESTAMP)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            print(f"An error occurred while fetching conversation: {e}")
            return []
        

    
    @staticmethod
    async def get_all_senders(db: AsyncSession) -> list[str]:
        """Get a list of all distinct senders (user IDs)"""
        try:
            result = await db.execute(
                select(distinct(CHAT_HISTO.SENDER))
                .where(CHAT_HISTO.SENDER != os.getenv("PHONE_NUMBER_ID"))
                .order_by(CHAT_HISTO.SENDER)
            )
            senders = result.scalars().all()
            return senders
        except SQLAlchemyError as e:
            print(f"An error occurred while fetching senders: {e}")
            return []






