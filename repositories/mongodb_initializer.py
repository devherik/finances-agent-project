"""
MongoDB database initialization utilities.

This module provides utility functions to initialize the MongoDB database
with proper collections, indexes, and validation schemas. It follows Clean
Architecture by separating database setup concerns and providing a clean
interface for database initialization.

The utilities ensure:
- Collections are created in the correct dependency order
- Proper indexes are applied for optimal performance
- Validation schemas are enforced for data integrity
- Referential integrity rules are documented for application-level enforcement
"""

from typing import Any, Dict
import logging
from pymongo.database import Database
from pymongo.errors import CollectionInvalid, OperationFailure
from repositories.mongodb_schema import MongoDBSchema, MongoDBCollections


class MongoDBInitializer:
    """
    MongoDB database initialization utility.
    
    This class follows the Single Responsibility Principle by focusing
    solely on database initialization and setup operations.
    """

    def __init__(self, database: Database):
        """
        Initialize the MongoDB initializer.
        
        Args:
            database: The MongoDB database instance
        """
        self.database = database
        self.logger = logging.getLogger(__name__)
        self.schema = MongoDBSchema()

    def initialize_database(self, drop_existing: bool = False) -> bool:
        """
        Initialize the entire database with collections, indexes, and validation.
        
        Args:
            drop_existing: Whether to drop existing collections before creating new ones
            
        Returns:
            bool: True if initialization was successful, False otherwise
            
        Note: This method orchestrates the entire database setup process,
        ensuring proper dependency order and error handling.
        """
        try:
            if drop_existing:
                self._drop_all_collections()
            
            # Create collections in dependency order
            self._create_collections()
            
            # Apply validation schemas
            self._apply_validation_schemas()
            
            # Create indexes for performance
            self._create_indexes()
            
            self.logger.info("Database initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False

    def _drop_all_collections(self) -> None:
        """Drop all existing collections."""
        collection_names = self.database.list_collection_names()
        for name in collection_names:
            if name in [
                MongoDBCollections.USERS,
                MongoDBCollections.ACCOUNTS,
                MongoDBCollections.TRANSACTION_CATEGORIES,
                MongoDBCollections.TRANSACTIONS
            ]:
                self.database[name].drop()
                self.logger.info(f"Dropped collection: {name}")

    def _create_collections(self) -> None:
        """
        Create collections in dependency order.
        
        This ensures that referenced collections exist before
        collections that reference them are created.
        """
        creation_order = self.schema.get_collection_creation_order()
        
        for collection_name in creation_order:
            try:
                self.database.create_collection(collection_name)
                self.logger.info(f"Created collection: {collection_name}")
            except CollectionInvalid:
                # Collection already exists
                self.logger.info(f"Collection already exists: {collection_name}")

    def _apply_validation_schemas(self) -> None:
        """Apply validation schemas to collections."""
        schemas = self.schema.get_collection_schemas()
        
        for collection_name, schema in schemas.items():
            try:
                self.database.command("collMod", collection_name, validator=schema)
                self.logger.info(f"Applied validation schema to: {collection_name}")
            except OperationFailure as e:
                self.logger.warning(f"Failed to apply validation to {collection_name}: {e}")

    def _create_indexes(self) -> None:
        """Create indexes for all collections."""
        indexes = self.schema.get_collection_indexes()
        
        for collection_name, index_list in indexes.items():
            collection = self.database[collection_name]
            try:
                # Drop existing indexes (except _id)
                collection.drop_indexes()
                
                # Create new indexes
                if index_list:
                    collection.create_indexes(index_list)
                    self.logger.info(f"Created {len(index_list)} indexes for: {collection_name}")
            except OperationFailure as e:
                self.logger.warning(f"Failed to create indexes for {collection_name}: {e}")

    def verify_setup(self) -> Dict[str, Any]:
        """
        Verify that the database setup is correct.
        
        Returns:
            Dict containing verification results for each collection
        """
        results = {}
        collections = [
            MongoDBCollections.USERS,
            MongoDBCollections.ACCOUNTS,
            MongoDBCollections.TRANSACTION_CATEGORIES,
            MongoDBCollections.TRANSACTIONS
        ]
        
        for collection_name in collections:
            results[collection_name] = self._verify_collection(collection_name)
        
        return results

    def _verify_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Verify a specific collection setup.
        
        Args:
            collection_name: Name of the collection to verify
            
        Returns:
            Dict containing verification details
        """
        collection = self.database[collection_name]
        
        # Check if collection exists
        exists = collection_name in self.database.list_collection_names()
        
        # Get index information
        indexes = []
        if exists:
            indexes = [index["name"] for index in collection.list_indexes()]
        
        # Check document count
        count = collection.count_documents({}) if exists else 0
        
        return {
            "exists": exists,
            "indexes": indexes,
            "document_count": count,
            "status": "OK" if exists else "MISSING"
        }

    def create_sample_data(self) -> bool:
        """
        Create sample data for testing purposes.
        
        Returns:
            bool: True if sample data was created successfully
            
        Note: This is useful for development and testing environments.
        """
        try:
            # Sample user
            user_data = {
                "id": "user_001",
                "phone": "+1234567890",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
            
            # Sample category
            category_data = {
                "id": "cat_001",
                "name": "Food & Dining",
                "description": "Expenses related to food and dining",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
            
            # Sample account
            account_data = {
                "id": "acc_001",
                "user_id": "user_001",
                "account_type": "checking",
                "balance": 1000.0,
                "currency": "USD",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
            
            # Sample transaction
            transaction_data = {
                "id": "txn_001",
                "amount": 25.50,
                "currency": "USD",
                "status": "completed",
                "type": "expense",
                "date": "2024-01-01",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "description": "Lunch at restaurant",
                "category_id": "cat_001",
                "merchant": "Joe's Restaurant",
                "account_id": "acc_001",
                "user_id": "user_001"
            }
            
            # Insert sample data in dependency order
            self.database[MongoDBCollections.USERS].insert_one(user_data)
            self.database[MongoDBCollections.TRANSACTION_CATEGORIES].insert_one(category_data)
            self.database[MongoDBCollections.ACCOUNTS].insert_one(account_data)
            self.database[MongoDBCollections.TRANSACTIONS].insert_one(transaction_data)
            
            self.logger.info("Sample data created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create sample data: {e}")
            return False


def initialize_finance_database(database: Database, drop_existing: bool = False) -> bool:
    """
    Convenience function to initialize the finance database.
    
    Args:
        database: The MongoDB database instance
        drop_existing: Whether to drop existing collections
        
    Returns:
        bool: True if initialization was successful
        
    This function provides a simple interface following the
    Facade pattern to hide the complexity of database initialization.
    """
    initializer = MongoDBInitializer(database)
    return initializer.initialize_database(drop_existing=drop_existing)