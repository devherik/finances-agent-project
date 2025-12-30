from sqlalchemy.sql.functions import func
from sqlalchemy.future import select

from uuid import UUID
from typing import List
from datetime import datetime

from domain.repositories import IAccountRepository
from domain.entities.transactions_entities import (
    AccountBase,
    AccountCreate,
    AccountUpdate,
)

from infrastructure.repositories.base_sql_repo import SQLAlchemyRepository
from infrastructure.database.models import AccountModel


class AccountRepository(
    SQLAlchemyRepository[AccountModel, AccountBase, AccountCreate, AccountUpdate],
    IAccountRepository,
):
    async def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AccountBase]:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.db.execute(query)
        db_obj = result.scalars().all()
        if db_obj:
            return [self.domain_model.model_validate(obj) for obj in db_obj]
        return []

    async def get_balance_by_period(
        self, user_id: UUID, account_id: UUID, start_date: datetime, end_date: datetime
    ) -> float:
        query = (
            select(func.sum(self.model.balance))
            .where(self.model.user_id == user_id)
            .where(self.model.id == account_id)
            .where(self.model.date >= start_date)
            .where(self.model.date <= end_date)
        )
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            return db_obj
        return 0
