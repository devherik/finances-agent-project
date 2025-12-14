from sqlalchemy.future import select

from core.repositories import IUserRepository
from core.entities.user_entities import UserBase, UserCreate, UserUpdate
from infrastructure.repositories.base_sql_repo import SQLAlchemyRepository
