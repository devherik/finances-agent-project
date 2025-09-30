from agno.agent import Agent
from agno.exceptions import AgentRunException

from services.agent_service import AgentsService, IntentAnsweringTeam
from core.factories import create_mongo_db


async def main():

    agents_service: AgentsService = AgentsService(
        storage=create_mongo_db(table_name="agent_memory"),
        memory=True,
        model="gemini-2.5-flash",
        vector_db_factory=create_mongo_db
    )

    intent_answering_team = agents_service.get_intent_answering_team(
        session_id="session_12345"
    )

    try:
        while True:
            user_input = input("User: ")
            if user_input.lower() in {"exit", "quit"}:
                print("Exiting...")
                break

            response = run_agents_cicle(agents=intent_answering_team, user_input=user_input)
            print(f"Agent: {response if response else 'No response'}")
    except KeyboardInterrupt:
        print("\nExiting due to keyboard interrupt.")

def agent_response(agent: Agent, message: str, session_id: str) -> str:
     try:
         response = agent.run(message, session_id=session_id)
         if response.content:
             return response.content
         else:
             return "Agent did not return any content."
     except Exception as e:
         return f"Error during agent execution: {str(e)}"
     except AgentRunException as are:
         return f"Agent run exception: {str(are)}"
     
def run_agents_cicle(agents: IntentAnsweringTeam, user_input: str) -> str:
    try:
        intent_response = agent_response(agent=agents.intent_recognition_agent, message=user_input, session_id="session_12345")
        response_generated = agent_response(agent=agents.response_generation_agent, message=intent_response, session_id="session_12345")
        analyzed_response = agent_response(agent=agents.response_analysis_agent, message=response_generated, session_id="session_12345")
        return analyzed_response
    except Exception as e:
        return f"Error during agent execution: {str(e)}"
    except AgentRunException as are:
        return f"Agent run exception: {str(are)}"



if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
