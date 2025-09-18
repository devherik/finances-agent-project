from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text_helper(text: str, chunk_size: int) -> list[str]:
    """
    Splits text into chunks of a specified size.

    :param text: The text to split.
    :param chunk_size: The maximum size of each chunk.
    :return: A list of text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=100)
    return text_splitter.split_text(text)