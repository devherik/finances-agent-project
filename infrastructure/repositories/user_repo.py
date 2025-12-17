from typing import Optional
from sqlalchemy.future import select

from domain.repositories import IUserRepository
from domain.entities.user_entities import UserBase, UserCreate, UserUpdate
from infrastructure.repositories.base_sql_repo import SQLAlchemyRepository
from infrastructure.database.models import UserModel


class UserRepository(
    SQLAlchemyRepository[UserModel, UserBase, UserCreate, UserUpdate], IUserRepository
):
    """
    This class:
    1. Inherits logic from SQLAlchemyRepository (Code Reuse)
    2. Implements IUserRepository (Contract Fulfillment)
    """

    async def get_by_phone(self, phone: str) -> Optional[UserBase]:
        query = select(self.model).where(self.model.phone == phone)
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            return self.domain_model.model_validate(db_obj)
        return None

    async def get_by_email(self, email: str) -> Optional[UserBase]:
        query = select(self.model).where(self.model.email == email)
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            return self.domain_model.model_validate(db_obj)
        return None

    async def get_by_cpf(self, cpf: str) -> Optional[UserBase]:
        query = select(self.model).where(self.model.cpf == cpf)
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            return self.domain_model.model_validate(db_obj)
        return None

    async def get_by_cnpj(self, cnpj: str) -> Optional[UserBase]:
        query = select(self.model).where(self.model.cnpj == cnpj)
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            return self.domain_model.model_validate(db_obj)
        return None

    async def get_by_telegram_id(self, telegram_id: str) -> Optional[UserBase]:
        query = select(self.model).where(self.model.telegram_id == telegram_id)
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            return self.domain_model.model_validate(db_obj)
        return None
