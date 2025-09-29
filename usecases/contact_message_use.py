"""
Use case for validating contact information. It will evaluate the message and link or not to a account.
It will make search in the database for the user information and return it if it exists.
Also, it will 'map' the user message, finding the user intent, with means every time a message arrives to the webhook, this use case will be triggered.
"""

from models.models import User
from typing import Optional
from core.factories import create_mongo_db, create_agents_service


class ContactMessageUse:
    def __init__(self):
        
        pass

    async def filter_contact_message(self, phone_number: str, message: str) -> bool:
        # Here we will implement the logic to validate the contact information.
        # We will use a Intent Recognition model to identify the user intent.
        # The phone number will be used as the unique identifier for the user (session_id).
        # For now, we will just return True if the message contains "link" or "create"
        try:
            if not await self.is_user_existing(phone_number):
                new_user = User(phone=phone_number)
                # Here we would save the new user to the database
            else:
                return False
        except Exception as e:
            return False
        return False

    async def is_user_existing(self, phone_number: str) -> User | None:
        # Here we will implement the logic to check if the user exists in the database.
        # For now, we will just return False to simulate that the user does not exist.
        user: User | None = None
        try:
            # Simulate database lookup
            user = User(phone=phone_number) # Replace with actual DB call
            if not user:
                user = User(phone=phone_number)
                # Here we would save the new user to the database
            return user
        except Exception as e:
            ...
        return None
