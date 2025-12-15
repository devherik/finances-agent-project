from typing import Optional
from sqlalchemy.future import select

from domain.repositories import IUserRepository
from domain.entities.user_entities import UserBase, UserCreate, UserUpdate
from infrastructure.repositories.base_sql_repo import SQLAlchemyRepository


class UserRepository(
    SQLAlchemyRepository[UserBase, UserCreate, UserUpdate], IUserRepository
):
    """
    This class:
    1. Inherits logic from SQLAlchemyRepository (Code Reuse)
    2. Implements IUserRepository (Contract Fulfillment)
    """

    async def get_by_phone(self, phone: str) -> Optional[UserBase]:
        query = select(UserBase).where(UserBase.phone == phone)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[UserBase]:
        query = select(UserBase).where(UserBase.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_cpf(self, cpf: str) -> Optional[UserBase]:
        query = select(UserBase).where(UserBase.cpf == cpf)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_cnpj(self, cnpj: str) -> Optional[UserBase]:
        query = select(UserBase).where(UserBase.cnpj == cnpj)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_telegram_id(self, telegram_id: str) -> Optional[UserBase]:
        query = select(UserBase).where(UserBase.telegram_id == telegram_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
