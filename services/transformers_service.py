"""
Data transformers and output handlers for the ingestion workflow.

Transformers modify or enrich data, while outputs handle where
the processed data goes (vector database, files, etc.).
"""

from typing import List
from datetime import datetime
from agno.document.base import Document

from core.interfaces import IDataTransformer, IDataOutput, ProcessedData
from helpers.datetime_helper import get_current_date_context_helper
from helpers.json_dumper_helper import safe_json_dumps_helper


class MetadataEnricherTransformer(IDataTransformer):
    """
    Enriches metadata with additional context like timestamps,
    processing info, etc.
    """
    
    async def transform(self, data: List[ProcessedData]) -> List[ProcessedData]:
        """Add enriched metadata to all processed data"""
        print("Enriching metadata...", "INFO")
        
        date_context = get_current_date_context_helper()
        processing_timestamp = datetime.now().isoformat()
        
        for item in data:
            # Add processing metadata
            item.metadata.update({
                "processed_at": processing_timestamp,
                "processing_date_context": date_context,
                "content_length": len(item.content),
                "word_count": len(item.content.split()),
            })
            
            # Add source tracking
            item.source_info.update({
                "processed_at": processing_timestamp,
                "enrichment_applied": True
            })
            
        return data


class ContentCleanerTransformer(IDataTransformer):
    """
    Cleans and normalizes content for better processing.
    """
    
    async def transform(self, data: List[ProcessedData]) -> List[ProcessedData]:
        """Clean and normalize content"""
        print("Cleaning content...", "INFO")
        
        for item in data:
            # Clean the content
            cleaned_content = item.content.strip()
            cleaned_content = ' '.join(cleaned_content.split())  # Normalize whitespace
            
            # Remove very short chunks (likely noise)
            if len(cleaned_content) < 10:
                continue
                
            item.content = cleaned_content
            
            # Track cleaning applied
            item.metadata["content_cleaned"] = True
            item.metadata["original_length"] = len(item.content)

        return [item for item in data if len(item.content) >= 10] # Filter out too short chunks


class DocumentOutput(IDataOutput):
    """
    Converts processed data to agno Document objects for vector storage.
    """
    
    def __init__(self):
        self.documents: List[Document] = []
    
    async def output(self, data: List[ProcessedData]) -> bool:
        """Convert to Document objects"""
        print("Converting to Document objects...", "INFO")
        
        try:
            for i, item in enumerate(data):
                # Validate and clean the chunk_id to ensure it's database-friendly
                if not item.chunk_id:
                    print(f"Warning: Item {i} has no chunk_id, generating one...", "WARNING")
                    import uuid
                    clean_id = str(uuid.uuid4())
                else:
                    # Clean the chunk_id to remove any problematic characters
                    # Keep only alphanumeric, hyphens, and underscores
                    import re
                    clean_id = re.sub(r'[^a-zA-Z0-9_-]', '_', item.chunk_id)
                    
                    # Ensure the ID is not too long (database constraint)
                    if len(clean_id) > 255:
                        # Truncate and add a hash to maintain uniqueness
                        import hashlib
                        hash_suffix = hashlib.md5(clean_id.encode()).hexdigest()[:8]
                        clean_id = clean_id[:240] + "_" + hash_suffix
                
                if not item.content or not item.content.strip():
                    print(f"Warning: Item {i} has empty content, skipping...", "WARNING")
                    continue
                
                # Ensure metadata is a valid dictionary
                metadata = item.metadata if item.metadata else {}
                
                # Ensure metadata values are JSON serializable
                clean_metadata = {}
                for key, value in metadata.items():
                    try:
                        # Convert non-serializable types to strings
                        if isinstance(value, (str, int, float, bool, type(None))):
                            clean_metadata[key] = value
                        else:
                            clean_metadata[key] = str(value)
                    except Exception:
                        clean_metadata[key] = str(value)
                
                # Create agno Document with validated data
                doc = Document(
                    content=item.content,
                    id=clean_id,  # Use cleaned ID (parameter name is 'id', not 'document_id')
                    name=item.chunk_id,    # Use chunk_id as name for reference
                    meta_data=clean_metadata  # Use cleaned metadata
                )
                
                # Final validation
                if not doc.id:
                    print(f"Error: Document {i} has no ID after creation!", "ERROR")
                    continue
                    
                if not doc.content:
                    print(f"Error: Document {i} has no content after creation!", "ERROR")
                    continue
                    
                self.documents.append(doc)
                
                # Log first few documents for debugging
                if i < 3:
                    print(f"  Created Document {i}: ID='{doc.id}', Content length={len(doc.content)}", "DEBUG")
                
            print(f"Created {len(self.documents)} Document objects", "INFO")
            return len(self.documents) > 0
            
        except Exception as e:
            print(f"Error creating Document objects: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    def get_documents(self) -> List[Document]:
        """Get the created documents"""
        return self.documents


class FileOutput(IDataOutput):
    """
    Saves processed data to files for inspection or backup.
    """
    
    def __init__(self, output_path: str):
        self.output_path = output_path
    
    async def output(self, data: List[ProcessedData]) -> bool:
        """Save processed data to file"""
        print(f"Saving to file: {self.output_path}", "INFO")
        
        try:
            output_data = []
            for item in data:
                output_item = {
                    "chunk_id": item.chunk_id,
                    "document_id": item.document_id,
                    "content": item.content,
                    "metadata": item.metadata,
                    "source_info": item.source_info
                }
                output_data.append(output_item)
            
            # Save as JSON
            json_output = safe_json_dumps_helper(output_data)
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write(json_output)
                
            print(f"Saved {len(output_data)} items to {self.output_path}", "INFO")
            return True
            
        except Exception as e:
            print(f"Error saving to file: {e}", "ERROR")
            return False


class LoggingOutput(IDataOutput):
    """
    Logs processed data statistics for monitoring.
    """
    
    async def output(self, data: List[ProcessedData]) -> bool:
        """Log processing statistics"""
        print("=== Processing Statistics ===", "INFO")
        
        try:
            # Calculate statistics
            total_items = len(data)
            total_content_length = sum(len(item.content) for item in data)
            unique_documents = len(set(item.document_id for item in data))
            
            # Group by source type
            source_types = {}
            for item in data:
                source_type = item.source_info.get("type", "unknown")
                source_types[source_type] = source_types.get(source_type, 0) + 1
            
            # Log statistics
            print(f"Total processed items: {total_items}", "INFO")
            print(f"Unique documents: {unique_documents}", "INFO")
            print(f"Total content length: {total_content_length} characters", "INFO")
            print(f"Average chunk length: {total_content_length / total_items:.1f} characters", "INFO")
            print("Source type breakdown:", "INFO")
            for source_type, count in source_types.items():
                print(f"  {source_type}: {count} items", "INFO")
            
            return True
            
        except Exception as e:
            print(f"Error logging statistics: {e}", "ERROR")
            return False