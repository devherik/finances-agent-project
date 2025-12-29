from typing import List, Optional
from uuid import UUID

from domain.entities.transactions_entities import (
    AccountBase,
    AccountCreate,
    AccountUpdate,
)
from domain.repositories import IAccountRepository


class AccountService:
    """
    Service for managing financial accounts.

    This service acts as the Use Case layer for accounts, coordinating
    between the Controller/Tools and the Repository.
    """

    def __init__(self, repository: IAccountRepository):
        self.repository = repository

    async def create_account(self, account: AccountCreate) -> AccountBase:
        """
        Create a new account.

        Args:
            account: The account data to create

        Returns:
            The created account
        """
        return await self.repository.create(account)

    async def get_user_accounts(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AccountBase]:
        """
        Get all accounts for a specific user.

        Args:
            user_id: The ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of accounts
        """
        return await self.repository.get_by_user(user_id, skip, limit)

    async def get_account_balance(
        self, user_id: UUID, account_id: UUID
    ) -> Optional[float]:
        """
        Get the balance of a specific account.

        Note: The repository method assumes getting balance by period, but for now
        we might just returned the current balance from the account entity
        or use a specific repository method if available.
        Checking IAccountRepository, it has get_balance_by_period.
        However, the AccountBase entity has a 'balance' field.
        So getting the account by ID is sufficient to get the current balance.
        """
        account = await self.repository.get(account_id)
        if account and str(account.user_id) == str(user_id):
            return float(account.balance)
        return None

    async def get_account(self, account_id: UUID) -> Optional[AccountBase]:
        """
        Get an account by ID.

        Args:
            account_id: The ID of the account

        Returns:
            The account if found, None otherwise
        """
        return await self.repository.get(account_id)

    async def update_account(
        self, account_id: UUID, account_update: AccountUpdate
    ) -> Optional[AccountBase]:
        """
        Update an existing account.

        Args:
            account_id: The ID of the account to update
            account_update: The data to update

        Returns:
            The updated account if found, None otherwise
        """
        return await self.repository.update(account_id, account_update)
