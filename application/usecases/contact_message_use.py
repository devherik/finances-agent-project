"""
Use case for validating contact information. It will evaluate the message and link or not to a account.
It will make search in the database for the user information and return it if it exists.
Also, it will 'map' the user message, finding the user intent, with means every time a message arrives to the webhook, this use case will be triggered.
"""


from models.models import User
from typing import Optional
from core.factories import create_agents_service
from services.mongodb_manager import MongoDbManager
from services.agent_service import AgentsService
from repositories.mongodb_repository import MongoDBRepository
from helpers.loging_helper import logger


class ContactMessageUse:
    def __init__(self):
        try:
            self.db_manager = MongoDbManager()
            self.mongodb_repository = MongoDBRepository(self.db_manager.get_database())
            self.agents_service: AgentsService = create_agents_service()
        except Exception as e:
            logger.error(f"Error initializing ContactMessageUse: {e}")
            return None

    async def filter_contact_message(self, phone_number: str, message: str) -> bool:
        # Here we will implement the logic to validate the contact information.
        # We will use a Intent Recognition model to identify the user intent.
        # The phone number will be used as the unique identifier for the user (session_id).
        # For now, we will just return True if the message contains "link" or "create"

        try:
            user = await self.is_user_existing(phone_number)

            if user:
                logger.debug(f"User found: {user}")
                # Proceed with linking or other actions for existing user
                return True
            else:
                logger.info("No existing user found, creating new user.")
                new_user = await self.create_new_user(phone_number)
                if new_user:
                    logger.debug(f"New user created: {new_user}")
                    # Proceed with onboarding actions for new user
                    return True
                else:
                    logger.error("Failed to create new user.")
                    return False
        except Exception as e:
            logger.error(f"Error filtering contact message: {e}")
            return False

    async def is_user_existing(self, phone_number: str) -> User | None:
        # Here we will implement the logic to check if the user exists in the database.
        # For now, we will just return False to simulate that the user does not exist.
        user: User | None = None

        try:
            user: User | None = await self.mongodb_repository.get_user_by_phone(
                phone_number
            )

            if not user:
                user = User(phone=phone_number)
                id = await self.mongodb_repository.add_user(user)

                if id:
                    user.id = str(id)
                    logger.debug(f"New user created with ID: {user.id}")
                else:
                    logger.error("Failed to create new user.")
                    return None
            return user
        except Exception as e:
            logger.error(f"Error checking if user exists: {e}")
        return None

    async def create_new_user(self, phone_number: str) -> Optional[User]:
        
        try:
            new_user = User(phone=phone_number)
            user_id = await self.mongodb_repository.add_user(new_user)

            if user_id:
                new_user.id = str(user_id)
                logger.debug(f"New user created with ID: {new_user.id}")
                return new_user
            else:
                logger.error("Failed to create new user.")
                return None
        except Exception as e:
            logger.error(f"Error creating new user: {e}")
            return None
