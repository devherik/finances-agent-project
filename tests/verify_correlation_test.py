import asyncio
from core.context import set_correlation_id
from helpers.loging_helper import logger


async def main():
    print("--- Starting Correlation ID Verification ---")

    # Context 1
    cid1 = "test-correlation-id-1"
    set_correlation_id(cid1)
    logger.info("This log should have ID-1")

    # Context 2 (simulating another request in a different task if we were doing concurrency,
    # but here just overwriting to test basic mechanism)
    cid2 = "test-correlation-id-2"
    set_correlation_id(cid2)
    logger.info("This log should have ID-2")

    # Implicit check
    logger.success("Success message with implicit ID-2")


if __name__ == "__main__":
    asyncio.run(main())
