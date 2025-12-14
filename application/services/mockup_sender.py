from core.interfaces import ISenderMessage

class MockupSender(ISenderMessage):
    async def send(self, recipient: str, subject: str, body: str) -> bool:
        print(f"Mock sending message to {recipient} with subject '{subject}' and body '{body}'")
        return True