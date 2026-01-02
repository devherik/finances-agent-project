from infrastructure.repositories.agent_memory_repo import AgentMemoryRepository
from domain.entities.agent_entities import AgentRunCreate
import asyncio
import traceback

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from agno.agent import Agent

from core.settings import settings

from infrastructure.database.models import AccountModel
from infrastructure.repositories.account_repo import AccountRepository
from infrastructure.repositories.transaction_repo import TransactionRepository
from infrastructure.database.models import TransactionModel

from domain.factories import create_postgres_db
from domain.factories import create_pgvector_knowledge_db
from domain.factories import create_google_embedder
from domain.factories import create_google_model
from domain.entities.transactions_entities import (
    TransactionBase,
    AccountBase,
)

from helpers.loging_helper import logger
from helpers.uuid_handler import uuid_handler

from application.services.account_service import AccountService
from application.services.agent_service import AgentsService
from application.services.transaction_service import TransactionService
from application.tools.finance_tools import FinanceTools


prompt = """
# PERSONA: Financial Interaction Specialist (Agent Fi)
You are the AI Financial Representative for {{COMPANY_NAME}}. Your goal is to manage accounts receivable, clarify billing inquiries, and facilitate smooth B2B payment interactions with resellers.

# CORE PHILOSOPHY
Precision is non-negotiable. You are professional, transparent, and firm yet helpful. You prioritize maintaining the business relationship while ensuring financial accuracy.

# KNOWLEDGE BASE & CONTEXT
- **Company Identity:** {{COMPANY_NAME}} (B2B Skewer Manufacturer).
- **Target Audience:** Resellers (restaurants, event planners, supermarkets).
- **Interaction Scope:** Payment tracking, invoice explanation, credit limit inquiries, and collection reminders.

# RULES OF ENGAGEMENT
1. [cite_start]**Accuracy First:** Always verify numbers against the provided data before stating a balance[cite: 40].
2. **Confidentiality:** Do not disclose one client's financial data to another. 
3. [cite_start]**No Final Waivers:** You can suggest payment plans, but you must NEVER officially waive a debt or change a price without a "Human in the Loop" approval flag[cite: 39, 43].
4. **Professional Tone:** Use formal B2B language. Avoid slang. [cite_start]Use clear, bulleted lists for financial breakdowns[cite: 47, 58].

# INTERACTION PROTOCOL (Chain of Thought)
1. **Identify:** Recognize the user's intent (e.g., "I want to pay my bill" or "Why is this invoice higher?").
2. **Retrieve:** Look at the attached transaction history/ledger.
3. [cite_start]**Calculate:** If a sum is needed, calculate it step-by-step internally before responding[cite: 110].
4. **Respond:** Provide a clear summary of the status and a "Call to Action" (e.g., "Please send the receipt to [Email]").

# OUTPUT FORMAT
- Use Markdown for clarity.
- [cite_start]Tables for invoice lists or payment schedules[cite: 4, 36].
- Bold key dates and amounts.

# STOP RULE
If the user uses the phrase "MANUAL REVIEW," immediately summarize the current state of the conversation and inform the user that a human supervisor will take over.
"""


async def _get_engine():
    try:
        return create_async_engine(
            settings.get_async_postgres_url,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True,  # Verify connections before using them
            pool_size=5,  # Number of connections to maintain
            max_overflow=10,  # Additional connections when pool is exhausted
        )
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        traceback.print_exc()


async def _persist_agent_run(
    agent: Agent,
    user_id: str,
    user_input: str,
    response: AgentRunCreate,
    service: AgentsService,
):
    try:
        agent_run = AgentRunCreate(
            agent_name=agent.name,
            model_name=agent.model.id,
            user_id=user_id,
            prompt=user_input,
            input_context={"user_input": user_input},
            response=response.content,
        )
        try:
            await service.persist_agent_run(agent_run)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            traceback.print_exc()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        traceback.print_exc()


async def main():
    try:
        up_content = prompt.replace("{{COMPANY_NAME}}", "B2B Skewer Manufacturer")

        engine = await _get_engine()

        async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
        async with async_session() as session:
            t_repo = TransactionRepository(TransactionModel, TransactionBase, session)
            t_service = TransactionService(t_repo)

            a_repo = AccountRepository(AccountModel, AccountBase, session)
            a_service = AccountService(a_repo)

            arun_repo = AgentMemoryRepository(session)

            user_id = uuid_handler.string_to_uuid(
                "1a0fb514-d637-412b-b4a7-9d6bd2a09433"
            )

            service = AgentsService(
                storage=create_postgres_db(),
                memory=True,
                model=create_google_model(),
                repository=arun_repo,
                embedder_factory=create_google_embedder,
                vector_db_factory=create_pgvector_knowledge_db,
            )

            tools = FinanceTools(
                transaction_service=t_service,
                account_service=a_service,
                user_id=user_id,
            )

            agent: Agent = service.create_agent(
                name="Financial Interaction Specialist",
                model_id=settings.gemini_standard_model_name,
                role="Financial Interaction Specialist",
                instructions=up_content,
                tools=[tools],
            )

            response = await agent.arun(
                "Liste minhas contas e me mostre o saldo de cada uma.",
                user_id=uuid_handler.uuid_to_string(user_id),
                debug_mode=True,
            )
            print(f"Agent: {response.content}")

            await _persist_agent_run(
                agent,
                user_id,
                "Liste minhas contas e me mostre o saldo de cada uma.",
                response,
                service,
            )

            while True:
                user_input = input("User: ")
                if user_input.lower() == "exit":
                    break
                response = await agent.arun(
                    user_input,
                    user_id=uuid_handler.uuid_to_string(user_id),
                    debug_mode=True,
                )
                print(f"Agent: {response.content}")

                await _persist_agent_run(agent, user_id, user_input, response, service)

        await engine.dispose()

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        traceback.print_exc()
        await engine.dispose()

    except KeyboardInterrupt:
        logger.info("Agent run stopped by user.")
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
