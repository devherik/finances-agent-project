"""
Use case for validating contact information. It will evaluate the message and link or not to a account.
It will make search in the database for the user information and return it if it exists.
Here will be the user message 'map', with means every time a message arrives to the webhook, this use case will be triggered.
"""

class ContactMessageUse:
    
    def __init__(self):
        pass
    
    async def filter_contact_message(self, phone_number: str, message: str) -> bool:
        # Here we will implement the logic to validate the contact information.
        # The phone number will be used as the unique identifier for the user (session_id).
        # For now, we will just return True if the message contains "link" or "create"
        if "link" in message.lower() or "create" in message.lower():
            return True
        return False