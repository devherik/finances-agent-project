"""
Factory functions for creating concrete implementations.

This module provides factory functions that create concrete implementations
of our abstract interfaces. This follows the Dependency Inversion Principle
by allowing the application layer to depend on abstractions while the
infrastructure layer provides the concrete implementations.
"""

from typing import Any
from core.settings import settings
from agno.db.redis import RedisDb
from agno.memory.manager import 
from agno.models.openai import OpenAIChat
from agno.db.mongo import MongoDb
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge


def create_redis_storage() -> Any:
    """
    Factory function to create a Redis storage instance.
    
    Returns:
        RedisStorage: Configured Redis storage instance
    """
    return RedisStorage(
        prefix="celery",
        host="localhost",
        port=6379,
        db=1
    )


def create_redis_memory_db() -> Any:
    """
    Factory function to create a Redis memory database instance.
    
    Returns:
        RedisMemoryDb: Configured Redis memory database instance
    """
    return RedisDb(
        
    )


def create_openai_model(model_id: str = "gpt-4o-mini") -> Any:
    """
    Factory function to create a OpenAI model instance.

    Args:
        model_id: The model identifier to use
        
    Returns:
        OpenAIChat: Configured OpenAIChat model instance
    """
    return OpenAIChat(id=model_id, api_key=settings.openai_api_key)


def create_openai_embedder() -> Any:
    """
    Factory function to create a OpenAI embedder instance.
    
    Returns:
        OpenAIEmbedder: Configured OpenAI embedder instance
    """
    return OpenAIEmbedder(api_key=settings.openai_api_key)


def create_mongo_db(table_name: str) -> Any:
    """
    Factory function to create a MongoDB database instance.

    Args:
        table_name: Name of the table for the vector database
        
    Returns:
        MongoDb: Configured MongoDB database instance
    """
    return MongoDb(
        db_url=settings.mongodb_uri,
        db_name=settings.mongodb_database,
        knowledge_collection=table_name
    )


def create_agents_service() -> Any:
    """
    Factory function to create an AgentsService with all dependencies injected.
    
    This is the main factory that wires up all dependencies following
    the Dependency Injection pattern.
    
    Returns:
        AgentsService: Fully configured AgentsService instance
    """
    from services.agent_service import AgentsService
    
    return AgentsService(
        storage=create_redis_storage(),
        memory_db=create_redis_memory_db(),
        model=create_openai_model(),
        embedder_factory=create_openai_embedder,
        vector_db_factory=create_mongo_db
    )
    
def create_document_knowledge_base(table_name: str) -> Any:
    """
    Factory function to create a DocumentKnowledgeBase instance.
    
    Args:
        table_name: Name of the table for the vector database
        
    Returns:
        Knowledge: Configured Knowledge instance
    """
    return Knowledge(
        vector_db=create_mongo_db(table_name)
    )