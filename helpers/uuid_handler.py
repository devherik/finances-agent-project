"""
MongoDB UUID handling utilities.

This module provides utilities for properly handling UUIDs in MongoDB
following Clean Architecture principles. It addresses the UUID encoding
issues that occur when using native Python UUID objects with MongoDB.

The utilities ensure:
- Proper UUID serialization/deserialization for MongoDB
- Consistent string representation of UUIDs across the application
- Clean separation between domain models and database serialization
"""

from typing import Any, Dict
from uuid import UUID
import uuid


class UUIDHandler:
    """
    Handles UUID conversion for MongoDB operations.

    This class follows the Single Responsibility Principle by focusing
    solely on UUID serialization/deserialization concerns.
    """

    @staticmethod
    def uuid_to_string(obj: Any) -> str:
        """
        Convert UUID object to string representation.

        Args:
            obj: UUID object or string

        Returns:
            String representation of the UUID
        """
        if isinstance(obj, UUID):
            return str(obj)
        return obj

    @staticmethod
    def string_to_uuid(obj: Any) -> UUID:
        """
        Convert string to UUID object.

        Args:
            obj: String representation of UUID or UUID object

        Returns:
            UUID object
        """
        if isinstance(obj, str):
            return UUID(obj)
        return obj

    @staticmethod
    def prepare_for_mongodb(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a document for MongoDB insertion by converting UUIDs to strings.

        Args:
            data: Document dictionary that may contain UUID objects

        Returns:
            Document with UUIDs converted to strings

        Note: This follows the Interface Segregation Principle by providing
        a focused interface for MongoDB document preparation.
        """
        prepared_data = {}

        for key, value in data.items():
            if isinstance(value, UUID):
                # Convert UUID to string for MongoDB storage
                prepared_data[key] = str(value)
            elif isinstance(value, dict):
                # Recursively handle nested dictionaries
                prepared_data[key] = UUIDHandler.prepare_for_mongodb(value)
            elif isinstance(value, list):
                # Handle lists that might contain UUIDs
                prepared_data[key] = [
                    str(item) if isinstance(item, UUID) else item for item in value
                ]
            else:
                prepared_data[key] = value

        return prepared_data

    @staticmethod
    def restore_from_mongodb(
        data: Dict[str, Any], uuid_fields: list = None
    ) -> Dict[str, Any]:
        """
        Restore UUID objects from MongoDB document.

        Args:
            data: Document retrieved from MongoDB
            uuid_fields: List of field names that should be converted back to UUID objects

        Returns:
            Document with specified fields converted back to UUID objects
        """
        if uuid_fields is None:
            uuid_fields = ["id", "_id"]

        restored_data = data.copy()

        for field in uuid_fields:
            if field in restored_data and isinstance(restored_data[field], str):
                try:
                    restored_data[field] = UUID(restored_data[field])
                except (ValueError, TypeError):
                    # If conversion fails, keep as string
                    pass

        return restored_data


def generate_uuid_string() -> str:
    """
    Generate a new UUID as a string.

    Returns:
        String representation of a new UUID

    Note: This function provides a consistent way to generate
    string-based UUIDs across the application.
    """
    return str(uuid.uuid4())


def is_valid_uuid(uuid_string: str) -> bool:
    """
    Validate if a string is a valid UUID.

    Args:
        uuid_string: String to validate

    Returns:
        True if string is a valid UUID, False otherwise
    """
    try:
        UUID(uuid_string)
        return True
    except (ValueError, TypeError):
        return False


uuid_handler = UUIDHandler()
