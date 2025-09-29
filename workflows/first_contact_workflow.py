"""
This is the initial workflow for the finances agent project.
It will receive the first contact from the user and guide them through the process of setting up their finances.
At this point, the software have already searched for the user information in the database and
retrieved it if it exists. If the user does not exist, it will create a new user.
The workflow will then proceed to the next step, which is to gather more information about the user's finances.
"""
from typing import List, Any

from core.interfaces import IWorkflow, ISenderMessage
from services.mockup_sender import MockupSender
from models.models import User, Account, NewUser

class FirstContactWorkflow(IWorkflow):
    def __init__(self, session_id: str, sender: ISenderMessage = MockupSender()):
        self.steps: List[Any] = []
        self.session_id = session_id
        self.sender = sender

    def run(self, *args, **kwargs) -> bool:
        raise NotImplementedError("Synchronous run method is not implemented.")

    async def arun(self, phone_number: str | None, initial_message: str) -> str:
        
        # 1. Greet the user and introduce the agent
        inicial_messages = [
            "Hello! I'm your Finances Agent, here to help you manage your finances effectively.",
            "First, I need to gather some information to get started.\n",
            "Could you please provide your name and email address?"
        ]
        try:
            self.sender.send(
                recipient=phone_number,
                subject="Welcome to Finances Agent!",
                body="\n".join(inicial_messages)
            )
        except Exception as e:
            print(f"Failed to send welcome message: {e}")


        # 2. Ask for the user's name and email if not already provided
        # 3. Confirm the user's identity if information is found in the database
        # 4. Ask if the user wants to link any existing accounts or create new ones
