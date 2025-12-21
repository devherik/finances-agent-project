import asyncio
import traceback
from domain.entities.auth_entities import Credentials
from helpers.auth_helper import (
    get_password_hash,
    verify_password,
    create_access_token,
    validate_token,
)
from helpers.loging_helper import logger


async def main():
    try:
        logger.info("Starting Auth Flow Test...")

        # 1. Define Credentials
        logger.info("Defining credentials...")
        credentials = Credentials(
            email="herikupdated@gmail.com", password="strongpassword123"
        )
        logger.success(f"Credentials created for: {credentials.email}")
        logger.spacer()

        # 2. Validate Password (Simulation)
        # In a real flow, we would fetch the user from DB and compare the stored hash with input password.
        # Here we simulate that by hashing the input password first.
        logger.info("Simulating password storage and validation...")
        stored_hash = get_password_hash(credentials.password)

        # Verify the password
        is_valid = verify_password(credentials.password, stored_hash)
        assert is_valid, "Password validation failed!"
        logger.success("Password verified successfully.")
        logger.spacer()

        # 3. Create Token
        logger.info("Creating access token...")
        # Typically subject is the user identifier (e.g. email or username)
        access_token = create_access_token(data={"sub": credentials.email})
        assert access_token is not None, "Token creation failed!"
        logger.success(f"Token created: {access_token[:20]}...")
        logger.spacer()

        # 4. Retrieve/Validate Token
        logger.info("Validating token...")
        payload = validate_token(access_token)
        assert payload is not None, "Token validation failed!"
        assert payload.get("sub") == credentials.email, "Token subject mismatch!"
        logger.success(f"Token validated. User: {payload.get('sub')}")
        logger.spacer()

        logger.info("Auth Flow Test Completed Successfully.")

    except Exception as e:
        logger.error(f"Auth Flow Test Failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
