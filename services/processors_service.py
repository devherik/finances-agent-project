"""
Concrete implementations of data processors.

Each processor handles a specific data format, following the
Single Responsibility Principle and Open/Closed Principle.
"""

import json
import uuid
from typing import List
from pypdf import PdfReader

from core.interfaces import IDataProcessor, DataSource, ProcessedData, DataFormat
from helpers.chunck_text_helper import chunk_text_helper
from helpers.data_to_dict_helper import DataHandler


class JSONDataProcessor(IDataProcessor):
    """Processes JSON files and JSON data"""

    def can_process(self, source: DataSource) -> bool:
        return (source.format == DataFormat.JSON or
                (source.path is not None and source.path.endswith('.json')))

    async def process(self, source: DataSource) -> List[ProcessedData]:
        """Process JSON data with proper flattening and chunking"""
        print("Processing JSON data...", "INFO")

        try:
            # Load data
            if source.path:
                with open(source.path, "r", encoding="utf-8") as file:
                    data = json.load(file)
            else:
                data = source.data

            if not isinstance(data, list):
                data = [data]  # Wrap single objects in a list

        except Exception as e:
            print(f"Error reading JSON: {e}", "ERROR")
            return []

        processed_items = []
        data_handler = DataHandler()

        for idx, item in enumerate(data):
            try:
                # Flatten the data structure
                flat_metadata = data_handler.flatten(item)

                # Create text content for embedding
                text_content = " ".join([
                    f"{key}: {value}" for key, value in flat_metadata.items()
                    if value is not None
                ])

                # Chunk the text
                chunks = chunk_text_helper(text_content, chunk_size=384)

                # Create ProcessedData for each chunk
                document_id = str(uuid.uuid4())
                source_info = {
                    "type": "json",
                    "path": source.path or "in_memory",
                    "item_index": idx
                }

                for chunk_idx, chunk in enumerate(chunks):
                    chunk_id = f"{document_id}_chunk_{chunk_idx}"

                    processed_data = ProcessedData(
                        content=chunk,
                        metadata=flat_metadata,
                        source_info=source_info,
                        chunk_id=chunk_id,
                        document_id=document_id
                    )
                    processed_items.append(processed_data)

            except Exception as e:
                print(f"Error processing JSON item {idx}: {e}", "ERROR")
                continue

        return processed_items


class PDFDataProcessor(IDataProcessor):
    """Processes PDF files"""

    def can_process(self, source: DataSource) -> bool:
        return (source.format == DataFormat.PDF or
                (source.path is not None and source.path.endswith('.pdf')))

    async def process(self, source: DataSource) -> List[ProcessedData]:
        """Process PDF with page-by-page chunking"""
        print("Processing PDF data...", "INFO")

        if not source.path:
            print("PDF processing requires a file path", "ERROR")
            return []

        processed_items = []

        try:
            reader = PdfReader(source.path)
            document_id = str(uuid.uuid4())

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if not text.strip():
                    continue

                # Chunk the page text
                chunks = chunk_text_helper(text, chunk_size=384)

                source_info = {
                    "type": "pdf",
                    "path": source.path,
                    "page_number": page_num + 1,
                    "total_pages": len(reader.pages)
                }

                for chunk_idx, chunk in enumerate(chunks):
                    # Generate a clean, unique chunk ID
                    # Turn easy to searchable and sortable
                    # Format: {document_id}_page_{page_num:03d}_chunk_{chunk_idx:03d}
                    # Example: a1b2c3d4-e5f6-7890-abcd-ef1234567890_page_001_chunk_002
                    # Query example:
                    #-- Find all chunks from page 5
                    #SELECT * FROM vectors WHERE chunk_id LIKE '%_page_005_%';
                    chunk_id = f"{document_id}_page_{page_num:03d}_chunk_{chunk_idx:03d}"
                    
                    # Ensure chunk content is not empty
                    if not chunk.strip():
                        continue

                    processed_data = ProcessedData(
                        content=chunk.strip(),
                        metadata={
                            "page_number": page_num + 1,
                            "total_pages": len(reader.pages),
                            "source": source.path,
                            "chunk_index": chunk_idx,
                            "total_chunks_on_page": len(chunks)
                        },
                        source_info=source_info,
                        chunk_id=chunk_id,
                        document_id=document_id
                    )
                    processed_items.append(processed_data)

        except Exception as e:
            print(f"Error processing PDF: {e}", "ERROR")

        return processed_items


class RowsDataProcessor(IDataProcessor):
    """Processes lists of dictionaries (rows)"""

    def can_process(self, source: DataSource) -> bool:
        return (source.format == DataFormat.ROWS or
                (isinstance(source.data, list) and
                 all(isinstance(item, dict) for item in source.data)))

    async def process(self, source: DataSource) -> List[ProcessedData]:
        """Process rows with individual row processing"""
        print("Processing rows data...", "INFO")

        if not source.data:
            print("No data provided for rows processing", "ERROR")
            return []

        processed_items = []
        data_handler = DataHandler()

        for idx, row in enumerate(source.data):
            try:
                # Flatten the row
                flat_metadata = data_handler.flatten(row)

                # Create text content
                text_content = " ".join([
                    f"{key}: {value}" for key, value in flat_metadata.items()
                    if value is not None
                ])

                # Chunk the text
                chunks = chunk_text_helper(text_content, chunk_size=384)

                document_id = str(uuid.uuid4())
                source_info = {
                    "type": "rows",
                    "row_index": idx,
                    "total_rows": len(source.data)
                }

                for chunk_idx, chunk in enumerate(chunks):
                    chunk_id = f"{document_id}_row_{idx}_chunk_{chunk_idx}"

                    processed_data = ProcessedData(
                        content=chunk,
                        metadata=flat_metadata,
                        source_info=source_info,
                        chunk_id=chunk_id,
                        document_id=document_id
                    )
                    processed_items.append(processed_data)

            except Exception as e:
                print(f"Error processing row {idx}: {e}", "ERROR")
                continue

        return processed_items


class TextDataProcessor(IDataProcessor):
    """Processes plain text files"""

    def can_process(self, source: DataSource) -> bool:
        return (source.format == DataFormat.TXT or
                (source.path is not None and source.path.endswith('.txt')))

    async def process(self, source: DataSource) -> List[ProcessedData]:
        """Process plain text with simple chunking"""
        print("Processing text data...", "INFO")

        try:
            # Load text
            if source.path:
                with open(source.path, "r", encoding="utf-8") as file:
                    text = file.read()
            else:
                text = str(source.data)

        except Exception as e:
            print(f"Error reading text: {e}", "ERROR")
            return []

        processed_items = []

        try:
            # Chunk the text
            chunks = chunk_text_helper(text, chunk_size=384)

            document_id = str(uuid.uuid4())
            source_info = {
                "type": "text",
                "path": source.path or "in_memory",
                "original_length": len(text)
            }

            for chunk_idx, chunk in enumerate(chunks):
                chunk_id = f"{document_id}_chunk_{chunk_idx}"

                processed_data = ProcessedData(
                    content=chunk,
                    metadata={
                        "source": source.path or "in_memory",
                        "chunk_index": chunk_idx,
                        "total_chunks": len(chunks)
                    },
                    source_info=source_info,
                    chunk_id=chunk_id,
                    document_id=document_id
                )
                processed_items.append(processed_data)

        except Exception as e:
            print(f"Error processing text: {e}", "ERROR")

        return processed_items

class XLSXDataProcessor(IDataProcessor):
    """Processes XLSX files"""

    def can_process(self, source: DataSource) -> bool:
        return (source.format == DataFormat.XLSX or
                (source.path is not None and source.path.endswith('.xlsx')))

    async def process(self, source: DataSource) -> List[ProcessedData]:
        """Process XLSX data with proper flattening and chunking"""
        print("Processing XLSX data...", "INFO")

        try:
            import pandas as pd
        except ImportError:
            print("pandas library is required to process XLSX files. Please install it.", "ERROR")
            return []

        try:
            # Load data
            if source.path:
                df = pd.read_excel(source.path)
            else:
                print("XLSX processing requires a file path", "ERROR")
                return []

            data = df.to_dict(orient='records')

            if not isinstance(data, list):
                data = [data]  # Wrap single objects in a list

        except Exception as e:
            print(f"Error reading XLSX: {e}", "ERROR")
            return []

        processed_items = []
        data_handler = DataHandler()

        for idx, item in enumerate(data):
            try:
                # Flatten the data structure
                flat_metadata = data_handler.flatten(item)

                # Create text content for embedding
                text_content = " ".join([
                    f"{key}: {value}" for key, value in flat_metadata.items()
                    if value is not None
                ])

                # Chunk the text
                chunks = chunk_text_helper(text_content, chunk_size=384)

                # Create ProcessedData for each chunk
                document_id = str(uuid.uuid4())
                source_info = {
                    "type": "xlsx",
                    "path": source.path or "in_memory",
                    "item_index": idx
                }

                for chunk_idx, chunk in enumerate(chunks):
                    chunk_id = f"{document_id}_chunk_{chunk_idx}"

                    processed_data = ProcessedData(
                        content=chunk,
                        metadata=flat_metadata,
                        source_info=source_info,
                        chunk_id=chunk_id,
                        document_id=document_id
                    )
                    processed_items.append(processed_data)

            except Exception as e:
                print(f"Error processing XLSX item {idx}: {e}", "ERROR")
                continue

        return processed_items