import json
import uuid
from pypdf import PdfReader
from agno.document.base import Document
from helpers.chunck_text_helper import chunk_text_helper

async def embed_from_json(path: str) -> list[Document]:
    """
    Embeds a JSON object and returns the text to embed and the metadata payload.
    
    :param json: The JSON object to embed.
    :return: A list of Document objects.
    """
    print("Loading data from JSON...", "INFO")
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        print(f"Error reading {path}: {e}", "ERROR")
        data = []

    documents: list[Document] = []
    
    for _, item in enumerate(data):
        # Create text content and metadata for each item
        id = str(uuid.uuid4())
        text_to_embed = " ".join([str(item[key]) for key in item])
        metadata = {key: item[key] for key in item}
        metadata["source"] = file.name
        chunks = chunk_text_helper(text_to_embed, chunk_size=384)
        
        # Create a Document for each chunk
        for i, chunk in enumerate(chunks):
            document = Document(
                id=f"{id}_{i}_{chunk}",
                meta_data=metadata,
                name=f"{file.name}_chunk_{id}",
                content=chunk  # Use the actual text content, not embeddings
            )
            documents.append(document)
    return documents

async def embed_from_pdf(path: str) -> list[Document]:
    """
    Loads page content from a PDF file.

    :return: A list of Document objects.
    """
    print("Loading data from PDF...", "INFO")
    if not path.endswith('.pdf'):
        print(f"Provided path is not a PDF file: {path}", "ERROR")
        return []
    documents: list[Document] = []
    try:
        reader = PdfReader(path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                chunks = chunk_text_helper(text, chunk_size=384)
                for chunk in chunks:
                    id = str(uuid.uuid4())
                    documents.append(Document(
                        id=f"{id}_{chunk}",
                        meta_data={"source": path},
                        name=f"pdf_{len(documents)}",
                        content=chunk
                    ))
    except Exception as e:
        print(f"Error loading PDF data: {e}", "ERROR")
    return documents

async def embed_from_rows(rows: list[dict]) -> list[Document]:
    """
    Embeds data from a list of rows (dictionaries) and returns a list of Document objects.

    :param rows: List of rows to embed.
    :return: A list of Document objects.
    """
    print("Loading data from rows...", "INFO")
    documents: list[Document] = []

    for row in rows:
        id = str(uuid.uuid4())
        text_to_embed = " ".join([str(value) for value in row.values()])
        metadata = {key: str(row[key]) for key in row}
        metadata["source"] = "rows"
        chunks = chunk_text_helper(text_to_embed, chunk_size=384)

        for i, chunk in enumerate(chunks):
            document = Document(
                id=f"{id}_{i}_{chunk}",
                meta_data=metadata,
                name=f"row_{id}",
                content=chunk
            )
            documents.append(document)

    return documents