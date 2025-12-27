"""
Factory functions for creating concrete implementations.

This module provides factory functions that create concrete implementations
of our abstract interfaces. This follows the Dependency Inversion Principle
by allowing the application layer to depend on abstractions while the
infrastructure layer provides the concrete implementations.
"""

from core.settings import settings

from agno.models.google import Gemini
from agno.vectordb.pgvector import PgVector, SearchType
from agno.db.postgres import PostgresDb
from agno.db.redis import RedisDb
from agno.knowledge.embedder.google import GeminiEmbedder


def create_redis_memory_db() -> RedisDb:
    """
    Factory function to create a Redis memory database instance.

    Returns:
        RedisDb: Configured Redis memory database instance
    """
    return RedisDb(
        db_url=settings.get_redis_url,
    )


def create_google_model(model_id: str = "") -> Gemini:
    """
    Factory function to create a Google model instance.

    Args:
        model_id: The model identifier to use

    Returns:
        Gemini: Configured Gemini model instance
    """
    model_id = model_id or settings.gemini_standard_model_name
    return Gemini(
        id=model_id,
        api_key=settings.gemini_api_key,
        temperature=0.7,
        project_id=settings.gemini_project_id,
    )


def create_google_embedder() -> GeminiEmbedder:
    """
    Factory function to create a Google embedder instance.

    Returns:
        GeminiEmbedder: Configured Gemini embedder instance
    """
    return GeminiEmbedder(api_key=settings.gemini_api_key)


def create_postgres_db() -> PostgresDb:
    """
    Factory function to create a PostgreSQL database instance.

    Returns:
        PostgresDB: Configured PostgreSQL database instance
    """
    return PostgresDb(
        db_url=settings.get_postgres_url,
    )


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
        db_url=settings.get_postgres_url,
        table_name=table_name,
        search_type=SearchType.hybrid,
        embedder=create_google_embedder(),
    )
