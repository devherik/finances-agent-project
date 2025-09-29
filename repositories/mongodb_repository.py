"""Repository for MongoDB interactions."""

from pymongo.database import Database
from pymongo.errors import CollectionInvalid, OperationFailure

from helpers.loging_helper import logger
from models.models import User, Transaction, Account, TransactionCategory


class MongoDBRepository:
    def __init__(self, db: Database):
        self.db: Database = db

    # --- User operations ---
    async def get_user_by_phone(self, phone: str) -> User | None:
        try:
            data = self.db.users.find_one({"phone": phone})
            user: User | None = None
            if data:
                user = User.model_validate(data)
            return user
        except Exception as e:
            logger.error(f"Error retrieving user by phone {phone}: {e}")
            return None
        except CollectionInvalid as e:
            logger.error(f"Collection error: {e}")
            return None

    async def add_user(self, user_data: User) -> str | None:
        try:
            result = self.db.users.insert_one(user_data.model_dump())
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error adding user {user_data}: {e}")
            return None
        except OperationFailure as e:
            logger.error(f"Operation failure: {e}")
            return False

    async def update_user(self, phone: str, update_data: dict) -> bool:
        try:
            result = self.db.users.update_one({"phone": phone}, {"$set": update_data})
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user {phone} with data {update_data}: {e}")
            return False
        except OperationFailure as e:
            logger.error(f"Operation failure: {e}")
            return False

    async def delete_user(self, phone: str) -> bool:
        try:
            result = self.db.users.delete_one({"phone": phone})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user with phone {phone}: {e}")
            return False
        except OperationFailure as e:
            logger.error(f"Operation failure: {e}")
            return False

    # --- Account operations ---
    async def get_account_by_user_id(self, user_id: str):
        try:
            account = self.db.accounts.find_one({"user_id": user_id})
            return account
        except Exception as e:
            logger.error(f"Error retrieving account for user_id {user_id}: {e}")
            return None
        except CollectionInvalid as e:
            logger.error(f"Collection error: {e}")
            return None

    async def add_account(self, account_data: Account) -> str | None:
        try:
            result = self.db.accounts.insert_one(account_data.model_dump())
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error adding account {account_data}: {e}")
            return None
        except OperationFailure as e:
            logger.error(f"Operation failure: {e}")
            return False

    async def update_account(self, account_id: str, update_data: Account) -> bool:
        try:
            result = self.db.accounts.update_one(
                {"_id": account_id}, {"$set": update_data.model_dump()}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(
                f"Error updating account {account_id} with data {update_data}: {e}"
            )
            return False
        except OperationFailure as e:
            logger.error(f"Operation failure: {e}")
            return False

    async def delete_account(self, account_id: str) -> bool:
        try:
            result = self.db.accounts.delete_one({"_id": account_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting account {account_id}: {e}")
            return False
        except OperationFailure as e:
            logger.error(f"Operation failure: {e}")
            return False
