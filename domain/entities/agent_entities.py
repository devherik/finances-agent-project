from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict

from .enuns import AgentRunStatus


# Base Entity
class AgentRunBase(BaseModel):
    """
    Base attributes for an AI execution.
    """

    agent_name: str = Field(
        ..., description="The identifier of the agent (e.g., 'FinancialAdvisorBot')"
    )
    model_name: str = Field(
        ..., description="The specific LLM used (e.g., 'gpt-4o', 'claude-3-5-sonnet')"
    )
    user_id: UUID = Field(..., description="The user who triggered this run")

    # We use Dict to store complex contexts/prompts.
    # In a database like Postgres, this maps perfectly to JSONB.
    input_context: Dict[str, Any] = Field(
        default_factory=dict, description="The data fed into the agent"
    )


# Data Transfer Objects
class AgentRunCreate(AgentRunBase):
    """
    REQUEST: Created when the agent starts working.
    """

    pass


class AgentRunUpdate(BaseModel):
    """
    REQUEST: Used to patch the run record once the AI finishes.
    """

    status: AgentRunStatus
    output_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    # Analytics Metrics
    prompt_tokens: Optional[int] = Field(None, ge=0)
    completion_tokens: Optional[int] = Field(None, ge=0)
    execution_time_ms: Optional[int] = Field(
        None, ge=0, description="Time taken in milliseconds"
    )


class AgentRun(AgentRunBase):
    """
    ENTITY: The complete history of an AI interaction.
    """

    id: UUID = Field(default_factory=uuid4)
    status: AgentRunStatus = AgentRunStatus.STARTED

    output_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    # Cost & Performance Tracking
    prompt_tokens: int = 0
    completion_tokens: int = 0
    execution_time_ms: int = 0

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens
