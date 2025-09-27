"""
Example usage of MongoDB schema and initialization utilities.

This file demonstrates how to use the MongoDB schema definitions
and initialization utilities in a Clean Architecture context.
It serves as both documentation and a practical example for
database setup and usage.
"""

from core.factories import create_finance_db, initialize_finance_database
from repositories.mongodb_initializer import MongoDBInitializer
from repositories.mongodb_schema import MongoDBCollections
from models.models import User, Account


def setup_database_example():
    """
    Example of how to set up the database for the first time.
    
    This demonstrates the complete database initialization process
    following Clean Architecture principles.
    """
    print("Setting up finance database...")
    
    # Initialize the database with schema
    success = initialize_finance_database(drop_existing=False)
    
    if success:
        print("✅ Database initialized successfully!")
        
        # Verify the setup
        db = create_finance_db()
        initializer = MongoDBInitializer(db)
        verification_results = initializer.verify_setup()
        
        print("\n📊 Database Verification Results:")
        for collection, details in verification_results.items():
            status_emoji = "✅" if details["status"] == "OK" else "❌"
            print(f"{status_emoji} {collection}: {details['status']}")
            print(f"   - Indexes: {len(details['indexes'])}")
            print(f"   - Documents: {details['document_count']}")
        
        # Create sample data for testing
        print("\n🔄 Creating sample data...")
        sample_success = initializer.create_sample_data()
        print("✅ Sample data created!" if sample_success else "❌ Failed to create sample data")
        
    else:
        print("❌ Database initialization failed!")


def basic_usage_example():
    """
    Example of basic database operations using the schema.
    
    This demonstrates how to perform CRUD operations while
    maintaining referential integrity manually.
    """
    db = create_finance_db()
    
    # Example: Creating a new user
    print("Creating a new user...")
    user = User(
        id="user_002",
        phone="+1987654321",
        name="Jane Smith",
        email="jane.smith@example.com",
        created_at="2024-01-02T00:00:00Z",
        updated_at="2024-01-02T00:00:00Z"
    )
    
    # Insert using the Pydantic model's dict representation
    db[MongoDBCollections.USERS].insert_one(user.model_dump())
    print(f"✅ User created with ID: {user.id}")
    
    # Example: Creating an account for the user
    print("Creating an account...")
    account = Account(
        id="acc_002",
        user_id=user.id,  # Foreign key reference
        account_type="savings",
        balance=5000.0,
        currency="USD",
        created_at="2024-01-02T00:00:00Z",
        updated_at="2024-01-02T00:00:00Z"
    )
    
    db[MongoDBCollections.ACCOUNTS].insert_one(account.model_dump())
    print(f"✅ Account created with ID: {account.id}")
    
    # Example: Query with proper indexing
    print("Querying user's accounts...")
    user_accounts = list(db[MongoDBCollections.ACCOUNTS].find({"user_id": user.id}))
    print(f"📊 Found {len(user_accounts)} accounts for user {user.name}")


def advanced_query_examples():
    """
    Examples of advanced queries that benefit from the indexing strategy.
    
    These queries demonstrate how the schema design optimizes
    common financial application query patterns.
    """
    db = create_finance_db()
    
    print("🔍 Advanced Query Examples:")
    
    # 1. User's recent transactions (uses compound index: user_id + date)
    print("\n1. Recent transactions for a user:")
    recent_transactions = list(
        db[MongoDBCollections.TRANSACTIONS]
        .find({"user_id": "user_001"})
        .sort("date", -1)
        .limit(10)
    )
    print(f"   Found {len(recent_transactions)} recent transactions")
    
    # 2. Account balance tracking (uses compound index: account_id + date)
    print("\n2. Account transaction history:")
    account_history = list(
        db[MongoDBCollections.TRANSACTIONS]
        .find({"account_id": "acc_001"})
        .sort("date", -1)
    )
    print(f"   Found {len(account_history)} transactions for account")
    
    # 3. Spending analysis by category (uses category_id index)
    print("\n3. Spending by category:")
    pipeline = [
        {"$match": {"type": "expense", "user_id": "user_001"}},
        {"$group": {
            "_id": "$category_id",
            "total_amount": {"$sum": "$amount"},
            "transaction_count": {"$sum": 1}
        }},
        {"$sort": {"total_amount": -1}}
    ]
    
    spending_analysis = list(db[MongoDBCollections.TRANSACTIONS].aggregate(pipeline))
    print(f"   Analysis covers {len(spending_analysis)} categories")
    
    # 4. Monthly spending trends (uses compound index: user_id + type + date)
    print("\n4. Monthly spending trends:")
    monthly_pipeline = [
        {"$match": {"type": "expense", "user_id": "user_001"}},
        {"$group": {
            "_id": {"$substr": ["$date", 0, 7]},  # Extract YYYY-MM
            "monthly_total": {"$sum": "$amount"},
            "transaction_count": {"$sum": 1}
        }},
        {"$sort": {"_id": -1}}
    ]
    
    monthly_trends = list(db[MongoDBCollections.TRANSACTIONS].aggregate(monthly_pipeline))
    print(f"   Trends for {len(monthly_trends)} months")


if __name__ == "__main__":
    """
    Run examples demonstrating the MongoDB schema usage.
    """
    print("🏦 Finance Database Schema Examples")
    print("=" * 50)
    
    # Setup example
    setup_database_example()
    print("\n" + "=" * 50)
    
    # Basic usage example
    basic_usage_example()
    print("\n" + "=" * 50)
    
    # Advanced queries example
    advanced_query_examples()
    print("\n" + "=" * 50)
    print("✅ All examples completed!")