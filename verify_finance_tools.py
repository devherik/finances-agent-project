import asyncio
from decimal import Decimal
from typing import List, Optional
from uuid import uuid4, UUID

from application.services.transaction_service import TransactionService
from application.tools.finance_tools import FinanceTools
from domain.entities.transactions_entities import (
    TransactionCreate,
    TransactionBase,
    TransactionStatus,
    TransactionType,
)
from domain.repositories import ITransactionRepository


# Mock Repository
class MockTransactionRepository(ITransactionRepository):
    async def create(self, obj_in: TransactionCreate) -> TransactionBase:
        # Simulate DB creation
        return TransactionBase(**obj_in.model_dump())

    async def get(self, id: UUID) -> Optional[TransactionBase]:
        return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[TransactionBase]:
        return []

    async def update(self, id: UUID, obj_in) -> Optional[TransactionBase]:
        return None

    async def delete(self, id: UUID) -> bool:
        return True

    async def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[TransactionBase]:
        return [
            TransactionBase(
                id=uuid4(),
                user_id=str(user_id),
                amount=Decimal("100.00"),
                currency="USD",
                status=TransactionStatus.COMPLETED,
                type=TransactionType.EXPENSE,
                date="2025-12-28",
                created_at="2025-12-28T12:00:00",
                updated_at="2025-12-28T12:00:00",
                description="Test Transaction",
                merchant="Test Merchant",
                account_id="acc_123",
            )
        ]

    async def get_pending_incomes(self, user_id: UUID) -> List[TransactionBase]:
        return []


async def main():
    repo = MockTransactionRepository()
    service = TransactionService(repo)
    user_id = str(uuid4())
    tools = FinanceTools(transaction_service=service, user_id=user_id)

    print("Testing create_transaction...")
    result = await tools.create_transaction(
        amount=Decimal("50.00"),
        description="Coffee",
        merchant="Starbucks",
        account_id="acc_123",
    )
    print(result)

    print("\nTesting get_my_transactions...")
    txs = await tools.get_my_transactions()
    print(txs)


if __name__ == "__main__":
    asyncio.run(main())
