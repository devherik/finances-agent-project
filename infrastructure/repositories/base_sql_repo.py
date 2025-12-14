from typing import Type, TypeVar, Generic, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from domain.repositories import UpdateT, CreateT

# We assume you have SQLAlchemy models defined (Mapping Pydantic to DB Tables)
# Let's call the generic DB model "ModelType"
ModelType = TypeVar("ModelType")


class SQLAlchemyRepository(Generic[ModelType, CreateT, UpdateT]):
    """
    The 'Real World' implementation.
    This class depends on SQLAlchemy logic.
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, obj_in: CreateT) -> ModelType:
        # Convert Pydantic model to SQLAlchemy Dict
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get(self, id: UUID) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(self, id: UUID, obj_in: UpdateT) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            return None
        for field, value in obj_in.model_dump().items():
            setattr(db_obj, field, value)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: UUID) -> bool:
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.commit()
        return True
