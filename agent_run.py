import asyncio
import traceback

from agno.agent import Agent
from agno.memory import MemoryManager

from domain.factories import create_google_model
from domain.factories import create_postgres_db
from domain.factories import create_redis_memory_db

from helpers.loging_helper import logger


async def main():
    try:
        db = create_postgres_db()
        memory = MemoryManager(
            db=create_redis_memory_db(),
            model=create_google_model(),
        )
        model = create_google_model()
        agent = Agent(
            model=model,
            instructions="",
            name="",
            markdown=True,
            db=db,
            memory_manager=memory,
            enable_agentic_memory=True,
            cache_session=True,
            search_session_history=True,
            add_memories_to_context=True,
        )
        response = agent.run("What is a binary search tree? And how does it work?")
        metrics = {
            "duration": response.metrics.duration,
            "input_tokens": response.metrics.input_tokens,
            "output_tokens": response.metrics.output_tokens,
            "total_tokens": response.metrics.total_tokens,
            "cache_read_tokens": response.metrics.cache_read_tokens,
            "cache_write_tokens": response.metrics.cache_write_tokens,
            "cost": response.metrics.cost,
        }
        logger.info("Agent response:")
        logger.info(response.content)
        logger.spacer()
        logger.info("Metrics:")
        logger.info(metrics)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
