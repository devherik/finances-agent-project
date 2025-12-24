from typing import List
from uuid import UUID
from sqlalchemy.future import select

from domain.repositories import IAgentRunRepository
from domain.entities.agent_entities import (
    AgentRunBase,
    AgentRunCreate,
    AgentRunUpdate,
)
from infrastructure.repositories.base_sql_repo import SQLAlchemyRepository
from infrastructure.database.models import AgentRunModel


class AgentRunRepository(
    SQLAlchemyRepository[AgentRunModel, AgentRunBase, AgentRunCreate, AgentRunUpdate],
    IAgentRunRepository,
):
    """
    SQLAlchemy implementation for Agent Run Repository.
    """

    async def get_runs_by_session(self, session_id: str) -> List[AgentRunBase]:
        """
        Retrieves agent runs for a specific session.
        Note: The AgentRunModel currently does not have a 'session_id' column in the provided schema.
        Assuming 'input_context' might contain session_id or needing a schema update.
        For now, checking if 'session_id' is a field or if we should filter by something else.
        If 'session_id' is expected to be a column, the model needs an update.

        Based on current model, we might need to filter inside the JSONB input_context or add a column.
        Let's assume for now we search within input_context for session_id.
        """
        # Option 1: Search in JSONB (Postgres specific)
        # query = select(self.model).where(self.model.input_context['session_id'].astext == session_id)

        # Option 2: Pending Schema Update.
        # Given the instruction "implement... following pattern", and I cannot change model easily without migration,
        # I will implement a placeholder or best-effort query.

        # Checking model definition again...
        # id, user_id, agent_name, model_name, input_context...

        # If the user explicitly defined this interface, they likely expect the column or data to exist.
        # I will implement filtering by input_context assuming it's a JSON field.

        query = select(self.model).where(
            self.model.input_context["session_id"].astext == session_id
        )
        result = await self.db.execute(query)
        db_objs = result.scalars().all()
        return [self.domain_model.model_validate(obj) for obj in db_objs]
