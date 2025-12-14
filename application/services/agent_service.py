from typing import Optional, Callable, Any
from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
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

@dataclass
class IntentAnsweringTeam:
    """
    Represents the intent answering team with specialized AI agents for handling user intents.
    This class groups together agents responsible for different aspects of intent management,
    adhering to the Single Responsibility Principle by separating concerns into distinct agents.
    """
    intent_recognition_agent: Agent
    response_generation_agent: Agent
    response_analysis_agent: Agent

class AgentsService:
    """
    Service for creating and managing AI agents.
    
    This service follows Clean Architecture principles by depending on abstractions
    rather than concrete implementations, making it testable and flexible.
    """

    def __init__(self, 
                 storage: Any,  # agno.storage.base.Storage
                 memory: bool,  # when True, enables agentic memory  
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
        self.memory = memory
        self.model = model
        self.embedder_factory = embedder_factory
        self.vector_db_factory = vector_db_factory

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
        
        from agno.models.google import Gemini
        from core.settings import settings

        model_instance = Gemini(id=model_id, api_key=settings.gemini_api_key)

        # Create base agent configuration
        base_config = {
            "name": name,
            "role": role,
            "model": model_instance,
            "enable_agentic_memory": self.memory,
            "db": self.storage,
            "tools": tools,
            "instructions": instructions,
            "session_id": session_id,
            "search_history_sessions": True,
            "enable_user_memories": True,
        }
        
        # Add knowledge base if specified (following polymorphism)
        if knowledge_base_table and self.vector_db_factory and self.embedder_factory:
            base_config["knowledge"] = self._create_knowledge_base(
                knowledge_base_table, max_documents
            )
            base_config["search_knowledge"] = True
        
        return Agent(**base_config)
    
    def create_reasoning_agent(self, 
                             model_id: str,
                             role: str,
                             instructions: str,
                             name: str,
                             max_documents: int = 5,
                             knowledge_base_table: str = "",
                             tools: list = [],
                             session_id: str = "") -> Agent:
        """
        Create a reasoning agent with the specified configuration.
        This method uses the factory pattern to create reasoning agents with different configurations.
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
        from agno.models.google import Gemini
        from core.settings import settings

        model_instance = Gemini(id=model_id, api_key=settings.gemini_api_key)
        reasoning_agent = self.create_agent(
            model_id="gemini-2.5-pro",
            role=role,
            instructions=instructions,
            name=name,
            max_documents=max_documents,
            knowledge_base_table=knowledge_base_table,
            tools=tools,
            session_id=session_id
        )

        # Create base agent configuration
        base_config = {
            "name": name,
            "role": role,
            "model": model_instance,
            "enable_agentic_memory": self.memory,
            "db": self.storage,
            "tools": tools,
            "instructions": instructions,
            "session_id": session_id,
            "search_history_sessions": True,
            "enable_user_memories": True,
            "reasoning": True,
            "reasoning_agent": reasoning_agent,
            "reasoning_model": "gemini-2.5-pro",
            "reasoning_min_steps": 1,
            "reasoning_max_steps": 5,
        }
        
        # Add knowledge base if specified (following polymorphism)
        if knowledge_base_table and self.vector_db_factory and self.embedder_factory:
            base_config["knowledge"] = self._create_knowledge_base(
                knowledge_base_table, max_documents
            )
            base_config["search_knowledge"] = True
        
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
    
    def get_intent_answering_team(self, session_id: str = "") -> IntentAnsweringTeam:
        """
        Create and return an IntentAnsweringTeam with specialized agents.
        
        This method encapsulates the creation logic for the intent answering team,
        adhering to the Single Responsibility Principle by keeping team creation
        separate from other service logic.
        
        Args:
            session_id: Optional session identifier for agent memory

        Returns:
            IntentAnsweringTeam: Configured team of agents for intent answering
        """
        intent_recognition_agent = self.create_agent(
            model_id="gemini-2.5-flash-lite",
            role="user_intent_recognizer",
            instructions="Recognize user intent from messages.",
            name="Intent Recognition Agent",
            session_id=session_id
        )

        response_generation_agent = self.create_agent(
            model_id="gemini-2.5-flash",
            role="response_generator",
            instructions="Generate responses based on user intent.",
            name="Response Generation Agent",
            session_id=session_id
        )

        response_analysis_agent = self.create_agent(
            model_id="gemini-2.5-flash",
            role="feedback_analyzer",
            instructions="Analyze user feedback for improvements.",
            name="Feedback Analysis Agent",
            session_id=session_id
        )

        return IntentAnsweringTeam(
            intent_recognition_agent=intent_recognition_agent,
            response_generation_agent=response_generation_agent,
            response_analysis_agent=response_analysis_agent
        )