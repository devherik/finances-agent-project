import asyncio
from sqlalchemy import create_engine

from core.settings import settings
from domain.repositories import IUserRepository
from domain.entities.user_entities import UserBase, UserCreate
from infrastructure.repositories.user_repo import UserRepository


async def get_db():
    engine = create_engine(settings.get_postgres_url)
    return engine


async def main():
    db = await get_db()
    user_repository: IUserRepository = UserRepository(db, UserBase)
    await user_repository.create(
        UserCreate(
            name="Herik Rezende",
            email="herikrezende@gmail.com",
            cpf="12345678901",
            cnpj="12345678901234",
            phone="12345678901",
        )
    )

    await user_repository.get("1")

    await user_repository.delete("1")


if __name__ == "__main__":
    asyncio.run(main())
