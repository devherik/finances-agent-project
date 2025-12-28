"""
This is the initial workflow for the finances agent project.
It will receive the first contact from the user and guide them through the process of setting up their finances.
At this point, the software have already searched for the user information in the database and
retrieved it if it exists. If the user does not exist, it will create a new user.
The workflow will then proceed to the next step, which is to gather more information about the user's finances.
"""

from typing import List, Any

from domain.interfaces import IWorkflow

from helpers.loging_helper import logger


class FirstContactWorkflow(IWorkflow):
    def __init__(self, session_id: str):
        self.steps: List[Any] = []
        self.session_id = session_id

    def run(self, *args, **kwargs) -> bool:
        raise NotImplementedError("Synchronous run method is not implemented.")

    async def arun(self, phone_number: str | None, initial_message: str) -> None:
        try:
            messages = [
                "Hello! I'm your Finances Agent, here to help you manage your finances effectively.",
                "First, I need to gather some information to get started.\n",
                "Could you please provide your name and email address?",
            ]
            print("\n".join(messages))
            while True:
                user_input = input("User: ")
                if user_input.lower() == "exit":
                    break
                # TODO: Process user input
                # TODO: Send user input to LLM
                # TODO: Get response from LLM
                # TODO: Send response to user
                # TODO: Save user input and response to database
                # TODO: Save user input and response to session
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")
