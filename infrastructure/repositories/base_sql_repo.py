from typing import Type, TypeVar, Generic, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# ORM Model (SQLAlchemy)
ORMModelType = TypeVar("ORMModelType")
# Domain Entity (Pydantic)
DomainModelType = TypeVar("DomainModelType")
# Schemas
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class SQLAlchemyRepository(
    Generic[ORMModelType, DomainModelType, CreateSchemaType, UpdateSchemaType]
):
    """
    The 'Real World' implementation.
    This class depends on SQLAlchemy logic and maps between ORM models and Domain Entities.
    """

    def __init__(
        self,
        model: Type[ORMModelType],
        domain_model: Type[DomainModelType],
        db: AsyncSession,
    ):
        self.model = model
        self.domain_model = domain_model
        self.db = db

    async def create(self, obj_in: CreateSchemaType) -> DomainModelType:
        # Convert Pydantic model to SQLAlchemy Dict
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return self.domain_model.model_validate(db_obj)

    async def get(self, id: UUID) -> Optional[DomainModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            return self.domain_model.model_validate(db_obj)
        return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[DomainModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        db_objs = result.scalars().all()
        return [self.domain_model.model_validate(obj) for obj in db_objs]

    async def update(
        self, id: UUID, obj_in: UpdateSchemaType
    ) -> Optional[DomainModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            return None
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return self.domain_model.model_validate(db_obj)

    async def delete(self, id: UUID) -> bool:
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.commit()
        return True
