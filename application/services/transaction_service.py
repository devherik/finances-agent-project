from datetime import datetime
from typing import List, Optional
from uuid import UUID

from domain.entities.transactions_entities import (
    TransactionBase,
    TransactionCreate,
    TransactionUpdate,
)
from domain.repositories import ITransactionRepository


class TransactionService:
    """
    Service for managing financial transactions.

    This service acts as the Use Case layer for transactions, coordinating
    between the Controller/Tools and the Repository.
    """

    def __init__(self, repository: ITransactionRepository):
        self.repository = repository

    async def create_transaction(
        self, transaction: TransactionCreate
    ) -> TransactionBase:
        """
        Create a new transaction.

        Args:
            transaction: The transaction data to create

        Returns:
            The created transaction
        """
        # Here we could add business logic, e.g., validation against user limits
        return await self.repository.create(transaction)

    async def get_transaction(self, transaction_id: UUID) -> Optional[TransactionBase]:
        """
        Get a transaction by ID.

        Args:
            transaction_id: The ID of the transaction to retrieve

        Returns:
            The transaction if found, None otherwise
        """
        return await self.repository.get(transaction_id)

    async def get_user_transactions(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[TransactionBase]:
        """
        Get all transactions for a specific user.

        Args:
            user_id: The ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of transactions
        """
        return await self.repository.get_by_user(user_id, skip, limit)

    async def get_balance_by_period(
        self, user_id: UUID, account_id: UUID, start_date: datetime, end_date: datetime
    ) -> float:
        return await self.repository.get_balance_by_period(
            user_id, account_id, start_date, end_date
        )

    async def get_transactions_by_text(
        self, user_id: UUID, text: str, skip: int = 0, limit: int = 100
    ) -> List[TransactionBase]:
        return await self.repository.get_transactions_by_text(
            user_id, text, skip, limit
        )

    async def get_pending_incomes(self, user_id: UUID) -> List[TransactionBase]:
        """
        Get pending income transactions for a user.

        Args:
            user_id: The ID of the user

        Returns:
            List of pending income transactions
        """
        return await self.repository.get_pending_incomes(user_id)

    async def update_transaction(
        self, transaction_id: UUID, transaction_update: TransactionUpdate
    ) -> Optional[TransactionBase]:
        """
        Update an existing transaction.

        Args:
            transaction_id: The ID of the transaction to update
            transaction_update: The data to update

        Returns:
            The updated transaction if found, None otherwise
        """
        return await self.repository.update(transaction_id, transaction_update)

    async def delete_transaction(self, transaction_id: UUID) -> bool:
        """
        Delete a transaction.

        Args:
            transaction_id: The ID of the transaction to delete

        Returns:
            True if deleted, False otherwise
        """
        return await self.repository.delete(transaction_id)
