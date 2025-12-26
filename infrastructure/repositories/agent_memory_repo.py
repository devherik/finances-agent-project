from sqlalchemy.sql.functions import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from typing import List

from domain.repositories import IAgentMemoryRepository
from domain.entities.agent_entities import AgentRunMemoryBase

from infrastructure.database.models import AgentMemoryModel


class AgentMemoryRepository(IAgentMemoryRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_interaction(
        self, user_id: UUID, prompt: str, response: str, embedding: List[float]
    ) -> None:
        """
        Saves the interaction and its embedding.
        Requires a 'memories' table with a vector column (pgvector).
        """
        memory = AgentMemoryModel(
            user_id=user_id,
            prompt=prompt,
            response=response,
            embedding=embedding,
        )
        self.db.add(memory)
        await self.db.commit()

    async def search_similar_interactions(
        self, user_id: UUID, embedding: List[float], k: int = 5
    ) -> List[AgentRunMemoryBase]:
        """
        Searches for similar interactions using vector similarity.
        """
        query = (
            select(AgentMemoryModel)
            .where(AgentMemoryModel.user_id == user_id)
            .order_by(func.l2_distance(AgentMemoryModel.embedding, embedding).asc())
            .limit(k)
        )
        result = await self.db.execute(query)
        db_obj = result.scalars().all()
        if db_obj:
            return [AgentRunMemoryBase.model_validate(obj) for obj in db_obj]
        return []
