import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from helpers.embedding_chunk_handler import embed_from_json, embed_from_rows
from core.settings import settings

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


async def main():
    print("--- Testing embed_from_json ---")
    docs_json = await embed_from_json("dummy_data.json")
    print(f"Generated {len(docs_json)} documents from JSON.")
    for doc in docs_json:
        print(f"Doc: {doc.content[:50]}... | Meta: {doc.meta_data}")

    print("\n--- Testing embed_from_rows ---")
    rows = [
        {"id": 101, "text": "Row data 1"},
        {"id": 102, "text": "Row data 2 is here"},
    ]
    docs_rows = await embed_from_rows(rows)
    print(f"Generated {len(docs_rows)} documents from Rows.")
    for doc in docs_rows:
        print(f"Doc: {doc.content[:50]}... | Meta: {doc.meta_data}")


if __name__ == "__main__":
    asyncio.run(main())
