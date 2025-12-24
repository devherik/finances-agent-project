from typing import List
from uuid import UUID
from sqlalchemy.future import select

from domain.repositories import ITransactionRepository
from domain.entities.transactions_entities import (
    TransactionBase,
    TransactionCreate,
    TransactionUpdate,
)
from infrastructure.repositories.base_sql_repo import SQLAlchemyRepository
from infrastructure.database.models import TransactionModel


class TransactionRepository(
    SQLAlchemyRepository[
        TransactionModel, TransactionBase, TransactionCreate, TransactionUpdate
    ],
    ITransactionRepository,
):
    """
    SQLAlchemy implementation for Transaction Repository.
    """

    async def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[TransactionBase]:
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        db_objs = result.scalars().all()
        return [self.domain_model.model_validate(obj) for obj in db_objs]

    async def get_pending_incomes(self, user_id: UUID) -> List[TransactionBase]:
        """
        Custom query for dashboarding.
        Assuming 'pending' status and 'income' type based on business logic.
        """
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.status == "PENDING",  # Adjust string literal if enum is mapped
            self.model.type == "INCOME",  # Adjust string literal if enum is mapped
        )
        result = await self.db.execute(query)
        db_objs = result.scalars().all()
        return [self.domain_model.model_validate(obj) for obj in db_objs]
