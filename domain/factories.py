"""
Factory functions for creating concrete implementations.

This module provides factory functions that create concrete implementations
of our abstract interfaces. This follows the Dependency Inversion Principle
by allowing the application layer to depend on abstractions while the
infrastructure layer provides the concrete implementations.
"""

from typing import Any

from core.settings import settings

from agno.agent import Agent
from agno.models.google import Gemini
from agno.vectordb.pgvector import PgVector, SearchType
from agno.vectordb.redis import RedisDB
from agno.knowledge.embedder.google import GeminiEmbedder


def create_redis_memory_db() -> RedisDB:
    """
    Factory function to create a Redis memory database instance.

    Returns:
        RedisDB: Configured Redis memory database instance
    """
    return RedisDB(
        redis_url=settings.get_redis_url,
        index_name=settings.get_redis_index_name,
        search_type=SearchType.vector,
    )


def create_google_model(model_id: str = "") -> Any:
    """
    Factory function to create a Google model instance.

    Args:
        model_id: The model identifier to use

    Returns:
        GoogleChat: Configured GoogleChat model instance
    """
    model_id = model_id or settings.gemini_standard_model_name
    return Gemini(
        id=model_id,
        api_key=settings.gemini_standard_model_name,
        temperature=0.7,
        project_id=settings.gemini_project_id,
    )


def create_google_embedder() -> GeminiEmbedder:
    """
    Factory function to create a Google embedder instance.

    Returns:
        GoogleEmbedder: Configured Google embedder instance
    """
    return GeminiEmbedder(api_key=settings.gemini_standard_model_name)


def create_pgvector_knowledge_db(table_name: str) -> PgVector:
    """
    Factory function to create a PostgreSQL database instance.

    Args:
        table_name: Name of the table for the vector database

    Returns:
        PgVector: Configured PostgreSQL database instance
    """
    table_name = table_name or "knowledge"
    return PgVector(
        db_url=settings.get_postgres_connection_string,
        table_name=table_name,
        search_type=SearchType.hybrid,
        embedder=create_google_embedder(),
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
        storage=None,  # Replace with actual storage implementation
        memory_db=create_redis_memory_db(),
        model=create_google_model(),
        embedder_factory=create_google_embedder,
        vector_db_factory=create_pgvector_knowledge_db,
    )
