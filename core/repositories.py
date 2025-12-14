from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from uuid import UUID

from entities.user_entities import User, UserCreate, UserUpdate
from entities.transaction_entities import (
    Transaction,
    TransactionCreate,
    TransactionUpdate,
)
from entities.agent_entities import AgentRun, AgentRunCreate, AgentRunUpdate

# We define a generic type T that must be a Pydantic Model (our Entities)
T = TypeVar("T")
CreateT = TypeVar("CreateT")
UpdateT = TypeVar("UpdateT")


class BaseRepository(ABC, Generic[T, CreateT, UpdateT]):
    """
    The Base Interface defining standard CRUD operations.
    Notice everything is 'async'. In FastAPI, this is critical for performance.
    """

    @abstractmethod
    async def create(self, obj_in: CreateT) -> T:
        """Creates a new record from the input model."""
        pass

    @abstractmethod
    async def get(self, id: UUID) -> Optional[T]:
        """Fetches a single record by ID."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Fetches a list of records with pagination."""
        pass

    @abstractmethod
    async def update(self, id: UUID, obj_in: UpdateT) -> Optional[T]:
        """Updates an existing record."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Deletes a record. Returns True if successful."""
        pass


# Implementations
class IUserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """
    Specific contract for User data access.
    """

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """
        Crucial for our bot: We need to find users by their Telegram ID, not just UUID.
        """
        pass

    @abstractmethod
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """
        Crucial for our bot: We need to find users by their phone, not just UUID.
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Crucial for our bot: We need to find users by their email, not just UUID.
        """
        pass

    @abstractmethod
    async def get_by_cpf(self, cpf: str) -> Optional[User]:
        """
        Crucial for our bot: We need to find users by their CPF, not just UUID.
        """
        pass

    @abstractmethod
    async def get_by_cnpj(self, cnpj: str) -> Optional[User]:
        """
        Crucial for our bot: We need to find users by their CNPJ, not just UUID.
        """
        pass


class ITransactionRepository(
    BaseRepository[Transaction, TransactionCreate, TransactionUpdate]
):
    """
    Specific contract for Financial Transactions.
    """

    @abstractmethod
    async def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        pass

    @abstractmethod
    async def get_pending_incomes(self, user_id: UUID) -> List[Transaction]:
        """Custom query for dashboarding."""
        pass


class IAgentRunRepository(BaseRepository[AgentRun, AgentRunCreate, AgentRunUpdate]):
    """
    Specific contract for AI Analytics.
    """

    @abstractmethod
    async def get_runs_by_session(self, session_id: str) -> List[AgentRun]:
        """Useful if we want to retrieve chat history context."""
        pass
