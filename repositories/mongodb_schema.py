"""
MongoDB schema definitions for the finance application.

This module defines the MongoDB collections, indexes, and validation rules
based on the Pydantic domain models. It follows Clean Architecture by
separating database schema concerns from domain models while ensuring
data integrity and optimal performance.

The schema design follows these principles:
- Single Responsibility: Each collection has a clear, focused purpose
- Database Normalization: Uses ID references to prevent data duplication
- Performance Optimization: Proper indexing for common queries
- Data Integrity: Validation rules to ensure consistency
"""

from typing import Dict, Any, List
from pymongo import IndexModel, ASCENDING, DESCENDING


class MongoDBCollections:
    """Constants for MongoDB collection names."""
    USERS = "users"
    ACCOUNTS = "accounts"
    TRANSACTION_CATEGORIES = "transaction_categories"
    TRANSACTIONS = "transactions"


class MongoDBSchema:
    """
    MongoDB schema definition and management.
    
    This class encapsulates all database schema operations, following the
    Single Responsibility Principle by focusing solely on schema management.
    It provides a clean interface for database initialization and maintenance.
    """

    @staticmethod
    def get_collection_schemas() -> Dict[str, Dict[str, Any]]:
        """
        Get MongoDB validation schemas for all collections.
        
        Returns:
            Dict mapping collection names to their validation schemas
            
        Note: These schemas enforce data integrity at the database level,
        complementing the Pydantic model validations in the application layer.
        """
        return {
            MongoDBCollections.USERS: {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["id", "phone", "name", "email", "created_at", "updated_at"],
                    "properties": {
                        "id": {
                            "bsonType": "string",
                            "description": "Unique identifier for the user"
                        },
                        "phone": {
                            "bsonType": "string",
                            "pattern": "^[+]?[0-9\\s\\-\\(\\)]+$",
                            "description": "Phone number of the user"
                        },
                        "name": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 100,
                            "description": "Name of the user"
                        },
                        "email": {
                            "bsonType": "string",
                            "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                            "description": "Email address of the user"
                        },
                        "created_at": {
                            "bsonType": "string",
                            "description": "Timestamp when the user was created"
                        },
                        "updated_at": {
                            "bsonType": "string",
                            "description": "Timestamp when the user was last updated"
                        },
                        "_id": {
                            "description": "MongoDB's automatically generated ObjectId"
                        }
                    },
                    "additionalProperties": False
                }
            },
            
            MongoDBCollections.ACCOUNTS: {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["id", "user_id", "account_type", "balance", "currency", "created_at", "updated_at"],
                    "properties": {
                        "id": {
                            "bsonType": "string",
                            "description": "Unique identifier for the account"
                        },
                        "user_id": {
                            "bsonType": "string",
                            "description": "Reference to the user who owns this account"
                        },
                        "account_type": {
                            "bsonType": "string",
                            "enum": ["savings", "checking", "credit", "investment", "loan"],
                            "description": "Type of the account"
                        },
                        "balance": {
                            "bsonType": "double",
                            "description": "Current balance of the account"
                        },
                        "currency": {
                            "bsonType": "string",
                            "pattern": "^[A-Z]{3}$",
                            "description": "Currency code (ISO 4217)"
                        },
                        "created_at": {
                            "bsonType": "string",
                            "description": "Timestamp when the account was created"
                        },
                        "updated_at": {
                            "bsonType": "string",
                            "description": "Timestamp when the account was last updated"
                        },
                        "_id": {
                            "description": "MongoDB's automatically generated ObjectId"
                        }
                    },
                    "additionalProperties": False
                }
            },
            
            MongoDBCollections.TRANSACTION_CATEGORIES: {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["id", "name", "description", "created_at", "updated_at"],
                    "properties": {
                        "id": {
                            "bsonType": "string",
                            "description": "Unique identifier for the transaction category"
                        },
                        "name": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 50,
                            "description": "Name of the transaction category"
                        },
                        "description": {
                            "bsonType": "string",
                            "maxLength": 255,
                            "description": "Description of the transaction category"
                        },
                        "created_at": {
                            "bsonType": "string",
                            "description": "Timestamp when the category was created"
                        },
                        "updated_at": {
                            "bsonType": "string",
                            "description": "Timestamp when the category was last updated"
                        },
                        "_id": {
                            "description": "MongoDB's automatically generated ObjectId"
                        }
                    },
                    "additionalProperties": False
                }
            },
            
            MongoDBCollections.TRANSACTIONS: {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "id", "amount", "currency", "status", "type", "date",
                        "created_at", "updated_at", "description", "category_id",
                        "merchant", "account_id", "user_id"
                    ],
                    "properties": {
                        "id": {
                            "bsonType": "string",
                            "description": "Unique identifier for the transaction"
                        },
                        "amount": {
                            "bsonType": "double",
                            "minimum": 0,
                            "description": "Amount of money involved in the transaction"
                        },
                        "currency": {
                            "bsonType": "string",
                            "pattern": "^[A-Z]{3}$",
                            "description": "Currency code (ISO 4217)"
                        },
                        "status": {
                            "bsonType": "string",
                            "enum": ["pending", "completed", "failed", "cancelled", "reversed"],
                            "description": "Current status of the transaction"
                        },
                        "type": {
                            "bsonType": "string",
                            "enum": ["expense", "income", "transfer", "credit", "debit", "investment"],
                            "description": "Type of the transaction"
                        },
                        "date": {
                            "bsonType": "string",
                            "description": "Date when the transaction occurred"
                        },
                        "created_at": {
                            "bsonType": "string",
                            "description": "Timestamp when the transaction was created"
                        },
                        "updated_at": {
                            "bsonType": "string",
                            "description": "Timestamp when the transaction was last updated"
                        },
                        "description": {
                            "bsonType": "string",
                            "maxLength": 255,
                            "description": "Description of the transaction"
                        },
                        "category_id": {
                            "bsonType": "string",
                            "description": "Reference to the transaction category"
                        },
                        "merchant": {
                            "bsonType": "string",
                            "maxLength": 100,
                            "description": "Merchant associated with the transaction"
                        },
                        "account_id": {
                            "bsonType": "string",
                            "description": "Reference to the account"
                        },
                        "user_id": {
                            "bsonType": "string",
                            "description": "Reference to the user"
                        },
                        "_id": {
                            "description": "MongoDB's automatically generated ObjectId"
                        }
                    },
                    "additionalProperties": False
                }
            }
        }

    @staticmethod
    def get_collection_indexes() -> Dict[str, List[IndexModel]]:
        """
        Get MongoDB indexes for all collections.
        
        Returns:
            Dict mapping collection names to their index definitions
            
        Note: These indexes are designed for optimal query performance
        based on common access patterns in financial applications.
        """
        return {
            MongoDBCollections.USERS: [
                IndexModel([("id", ASCENDING)], unique=True),
                IndexModel([("email", ASCENDING)], unique=True),
                IndexModel([("phone", ASCENDING)], unique=True),
                IndexModel([("created_at", DESCENDING)]),
            ],
            
            MongoDBCollections.ACCOUNTS: [
                IndexModel([("id", ASCENDING)], unique=True),
                IndexModel([("user_id", ASCENDING)]),  # Foreign key index
                IndexModel([("user_id", ASCENDING), ("account_type", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)]),
            ],
            
            MongoDBCollections.TRANSACTION_CATEGORIES: [
                IndexModel([("id", ASCENDING)], unique=True),
                IndexModel([("name", ASCENDING)], unique=True),
            ],
            
            MongoDBCollections.TRANSACTIONS: [
                IndexModel([("id", ASCENDING)], unique=True),
                IndexModel([("user_id", ASCENDING)]),  # Foreign key index
                IndexModel([("account_id", ASCENDING)]),  # Foreign key index
                IndexModel([("category_id", ASCENDING)]),  # Foreign key index
                IndexModel([("date", DESCENDING)]),  # For date range queries
                IndexModel([("created_at", DESCENDING)]),
                IndexModel([("status", ASCENDING)]),  # For filtering by status
                IndexModel([("type", ASCENDING)]),  # For filtering by type
                # Compound indexes for common query patterns
                IndexModel([("user_id", ASCENDING), ("date", DESCENDING)]),
                IndexModel([("account_id", ASCENDING), ("date", DESCENDING)]),
                IndexModel([("user_id", ASCENDING), ("status", ASCENDING), ("date", DESCENDING)]),
                IndexModel([("user_id", ASCENDING), ("type", ASCENDING), ("date", DESCENDING)]),
            ]
        }

    @staticmethod
    def get_referential_integrity_rules() -> Dict[str, List[str]]:
        """
        Get referential integrity rules for foreign key relationships.
        
        Returns:
            Dict mapping collection names to their foreign key fields
            
        Note: While MongoDB doesn't enforce referential integrity at the database level,
        this information is used by the application layer to maintain data consistency.
        """
        return {
            MongoDBCollections.ACCOUNTS: ["user_id"],
            MongoDBCollections.TRANSACTIONS: ["user_id", "account_id", "category_id"]
        }

    @classmethod
    def get_collection_creation_order(cls) -> List[str]:
        """
        Get the recommended order for creating collections.
        
        Returns:
            List of collection names in dependency order
            
        Note: Collections with no dependencies should be created first,
        followed by collections that reference them.
        """
        return [
            MongoDBCollections.USERS,
            MongoDBCollections.TRANSACTION_CATEGORIES,
            MongoDBCollections.ACCOUNTS,
            MongoDBCollections.TRANSACTIONS
        ]