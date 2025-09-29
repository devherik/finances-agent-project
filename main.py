import asyncio
from helpers.loging_helper import logger
from usecases.contact_validation_use import ContactValidationUse

async def main():
    logger.info("Hello from finances-agent-project!")
    initial_user_input = input()
    phone_number = "+1234567890"  # Example phone number
    try:
        while True:
            contact_validation = ContactValidationUse()
            if await contact_validation.validate_contact(phone_number, initial_user_input):
                logger.info("Valid contact information.")
            else:
                logger.warning("Invalid contact information.")
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
