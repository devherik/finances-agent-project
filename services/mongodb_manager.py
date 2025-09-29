from pymongo.database import Database
from pymongo.errors import CollectionInvalid, OperationFailure
from pymongo import MongoClient

from core.settings import settings
from helpers.loging_helper import logger


class MongoDbManager:
    """
    MongoDB Manager to handle database connections and operations.
    """

    def __init__(self):
        self.uri = settings.mongodb_uri
        self.db_name = settings.mongodb_database
        if not self.uri or not self.db_name:
            raise ValueError(
                "MongoDB URI and Database name must be provided in settings."
            )

    def create_mongo_db(self) -> Database:
        """
        Factory function to create a MongoDB database instance.

        Returns:
            Database: Configured MongoDB database instance
            
        Raises:
            ConnectionError: When MongoDB connection fails
            ValueError: When configuration is invalid
            
        Note: This method follows the Fail Fast principle - it's better
        to fail immediately with a clear error than to continue with
        invalid state.
        """
        try:
            client = MongoClient(settings.mongodb_uri)
            db = client[settings.mongodb_database]
            
            # Test the connection
            if self.test_connection(db):
                logger.info("Successfully connected to MongoDB.")
                return db
            else:
                logger.error("MongoDB connection test failed - database unreachable")
                raise ConnectionError(
                    f"Failed to connect to MongoDB at {settings.mongodb_uri}. "
                    "Please check your connection settings and ensure MongoDB is running."
                )
        except (CollectionInvalid, OperationFailure) as e:
            logger.error(f"MongoDB operation error: {e}")
            raise ConnectionError(f"MongoDB operation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise ConnectionError(f"Unexpected MongoDB connection error: {str(e)}")

    def test_connection(self, db: Database) -> bool:
        """
        Test the MongoDB connection.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            db.command("ping")
            logger.debug("MongoDB connection test successful.")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection test failed: {e}")
            return False
    
    def get_collection(self, db: Database, collection_name: str):
        """
        Get a collection from the database.

        Args:
            db: The MongoDB database instance.
            collection_name: Name of the collection to retrieve.

        Returns:
            Collection: The requested MongoDB collection.
        """
        try:
            collection = db[collection_name]
            logger.debug(f"Successfully retrieved collection: {collection_name}")
            return collection
        except Exception as e:
            logger.error(f"Error retrieving collection {collection_name}: {e}")
            raise