from typing import Optional, Callable, Any
from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.memory import MemoryManager
from dataclasses import dataclass
from helpers.datetime_helper import get_current_date_context_helper



@dataclass
class AnalyticsTeam:
    """
    Represents the analytics team with specialized AI agents for various tasks.
    This class groups together agents responsible for different stages of the analytics workflow,
    following the Single Responsibility Principle by separating concerns into distinct agents.
    """
    request_router_agent: Agent
    data_retrieval_agent: Agent
    data_processing_agent: Agent
    reporting_agent: Agent
    validation_agent: Agent

class AgentsService:
    """
    Service for creating and managing AI agents.
    
    This service follows Clean Architecture principles by depending on abstractions
    rather than concrete implementations, making it testable and flexible.
    """

    def __init__(self, 
                 storage: Any,  # agno.storage.base.Storage
                 memory_db: Any,  # agno.memory.v2.db.base.MemoryDb  
                 model: Any,  # agno.models.base.Model
                 embedder_factory: Optional[Callable[[], Any]] = None,
                 vector_db_factory: Optional[Callable[[str], Any]] = None):
        """
        Initialize AgentsService with injected dependencies.
        
        Args:
            storage: Storage implementation for agent persistence
            memory_db: Memory database for conversation history
            model: AI model for agent reasoning
            embedder_factory: Factory function to create embedder instances (optional)
            vector_db_factory: Factory function to create vector db instances (optional)
        """
        self.storage = storage
        self.memory_db = memory_db
        self.model = model
        self.embedder_factory = embedder_factory
        self.vector_db_factory = vector_db_factory
        self.memory = MemoryManager(db=self.memory_db, model=self.model)

    def create_agent(self, 
                     model_id: str,
                     role: str,
                     instructions: str,
                     name: str,
                     max_documents: int = 5,
                     knowledge_base_table: str = "",
                     tools: list = [],
                     session_id: str = "") -> Agent:
        """
        Create an agent with the specified configuration.
        
        This method uses the factory pattern to create agents with different configurations.
        It follows the Open/Closed Principle: you can extend agent types without modifying
        this method, just by providing different factories.
        
        Args:
            model_id: Identifier for the model to use
            role: Role description for the agent
            instructions: Instructions for the agent behavior
            name: Name of the agent
            max_documents: Maximum documents for knowledge base
            knowledge_base_table: Table name for vector database (optional)
            tools: List of tools available to the agent
            
        Returns:
            Configured Agent instance
        """
        # Create a new model instance for this agent
        # The model factory should be injected, but for now we create it directly
        # This is where you'd use your injected model factory in a full implementation
        from agno.models.openai import OpenAIChat
        from core.settings import settings

        model_instance = OpenAIChat(id=model_id, api_key=settings.openai_api_key)

        # Create base agent configuration
        base_config = {
            "name": name,
            "role": role,
            "model": model_instance,
            "memory": self.memory,
            "storage": self.storage,
            "show_tool_calls": True,
            "tools": tools,
            "instructions": instructions,
            "session_id": session_id,
            "add_history_to_messages": True,
        }
        
        # Add knowledge base if specified (following polymorphism)
        if knowledge_base_table and self.vector_db_factory and self.embedder_factory:
            base_config["knowledge"] = self._create_knowledge_base(
                knowledge_base_table, max_documents
            )
        
        return Agent(**base_config)
    
    def _create_knowledge_base(self, table_name: str, max_documents: int):
        """
        Private method to create knowledge base using injected factories.
        
        This demonstrates the Dependency Inversion Principle: we depend on
        the abstract factories, not concrete implementations.
        """
        if not self.vector_db_factory:
            raise ValueError("vector_db_factory is required for knowledge base creation")
            
        return Knowledge(
            max_results=max_documents,
            vector_db=self.vector_db_factory(table_name),
        )