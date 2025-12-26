import json
import uuid

from typing import List, Dict, Any
from starlette.concurrency import run_in_threadpool
from pypdf import PdfReader

from agno.knowledge.document import Document
from agno.knowledge.embedder.google import GeminiEmbedder

from helpers.chunck_text_helper import chunk_text_helper
from helpers.loging_helper import logger

from core.settings import settings

from domain.factories import create_google_embedder


def _load_json_file(path: str) -> List[Dict[str, Any]]:
    """Helper to load JSON file synchronously."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _extract_text_from_pdf(path: str) -> str:
    """Helper to extract text from PDF synchronously."""
    text_content = []
    reader = PdfReader(path)
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_content.append(text)
    return "\n".join(text_content)


def _get_embedding(text: str) -> List[float]:
    """Helper to get embedding synchronously."""
    embedder: GeminiEmbedder = create_google_embedder()
    return embedder.get_embedding(text)


async def embed_from_json(path: str) -> List[Document]:
    """
    Embeds a JSON object and returns the text to embed and the metadata payload.

    :param path: Path to the JSON file.
    :return: A list of Document objects.
    """
    logger.info("Loading data from JSON...")

    try:
        # Offload blocking I/O to threadpool
        data = await run_in_threadpool(_load_json_file, path)
    except Exception as e:
        logger.error(f"Error reading {path}: {e}", exc_info=True)
        return []

    documents: List[Document] = []
    file_name = path.split("/")[-1]  # Simple extraction, could be improved with os.path

    for _, item in enumerate(data):
        # Create text content and metadata for each item
        doc_id = str(uuid.uuid4())
        text_to_embed = " ".join([str(item[key]) for key in item])
        metadata = {key: item[key] for key in item}
        metadata["source"] = file_name

        chunks = chunk_text_helper(
            text_to_embed, chunk_size=settings.embedding_chunk_size
        )

        # Create a Document for each chunk
        for i, chunk in enumerate(chunks):
            document = Document(
                id=f"{doc_id}_{i}_{chunk}",
                meta_data=metadata,
                name=f"{file_name}_chunk_{doc_id}",
                embedding=_get_embedding(chunk),
                content=chunk,  # Use the actual text content, not embeddings
            )
            documents.append(document)

    return documents


async def embed_from_pdf(path: str) -> List[Document]:
    """
    Loads page content from a PDF file.

    :param path: Path to the PDF file.
    :return: A list of Document objects.
    """
    logger.info("Loading data from PDF...")

    if not path.endswith(".pdf"):
        logger.error(f"Provided path is not a PDF file: {path}")
        return []

    documents: List[Document] = []

    try:
        # Offload blocking I/O to threadpool
        full_text = await run_in_threadpool(_extract_text_from_pdf, path)

        if full_text:
            chunks = chunk_text_helper(
                full_text, chunk_size=settings.embedding_chunk_size
            )
            for i, chunk in enumerate(chunks):
                doc_id = str(uuid.uuid4())
                documents.append(
                    Document(
                        id=f"{doc_id}_{chunk}",  # Note: This ID format might be problematic if chunks are identical across diff runs without unique seed, but keeping close to original logic
                        meta_data={"source": path},
                        name=f"pdf_{len(documents)}",
                        embedding=_get_embedding(chunk),
                        content=chunk,
                    )
                )

    except Exception as e:
        logger.error(f"Error loading PDF data: {e}", exc_info=True)

    return documents


async def embed_from_rows(rows: List[Dict[str, Any]]) -> List[Document]:
    """
    Embeds data from a list of rows (dictionaries) and returns a list of Document objects.

    :param rows: List of rows to embed.
    :return: A list of Document objects.
    """
    logger.info("Loading data from rows...")
    documents: List[Document] = []

    for row in rows:
        doc_id = str(uuid.uuid4())
        text_to_embed = " ".join([str(value) for value in row.values()])
        metadata = {key: str(row[key]) for key in row}
        metadata["source"] = "rows"

        chunks = chunk_text_helper(
            text_to_embed, chunk_size=settings.embedding_chunk_size
        )

        for i, chunk in enumerate(chunks):
            document = Document(
                id=f"{doc_id}_{i}_{chunk}",
                meta_data=metadata,
                name=f"row_{doc_id}",
                embedding=_get_embedding(chunk),
                content=chunk,
            )
            documents.append(document)

    return documents
