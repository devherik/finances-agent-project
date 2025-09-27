#!/usr/bin/env python3
"""
Test script for UUID handling in MongoDB operations.

This script demonstrates and tests the UUID handling solution
to ensure it works properly with MongoDB operations.
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.factories import create_finance_db, initialize_finance_database
from repositories.mongodb_initializer import MongoDBInitializer
from repositories.mongodb_schema import MongoDBCollections
from repositories.uuid_handler import UUIDHandler, generate_uuid_string, is_valid_uuid
from models.models import User, Account


def test_uuid_handling():
    """Test UUID handling functionality."""
    print("🧪 Testing UUID Handling")
    print("=" * 50)
    
    # Test UUID generation
    test_uuid = generate_uuid_string()
    print(f"✅ Generated UUID: {test_uuid}")
    print(f"✅ UUID validation: {is_valid_uuid(test_uuid)}")
    
    # Test UUID handler
    test_user = User(
        phone="+1234567890",
        name="Test User",
        email="test@example.com",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z"
    )
    
    print(f"✅ User created with UUID: {test_user.id}")
    print(f"✅ UUID type: {type(test_user.id)}")
    
    # Test data preparation for MongoDB
    prepared_data = UUIDHandler.prepare_for_mongodb(test_user.model_dump())
    print(f"✅ Prepared data - ID type: {type(prepared_data['id'])}")
    print(f"✅ Prepared data - ID value: {prepared_data['id']}")
    
    return test_user, prepared_data


def test_database_operations():
    """Test database operations with UUID handling."""
    print("\n🗄️ Testing Database Operations")
    print("=" * 50)
    
    try:
        # Initialize database
        print("🔄 Initializing database...")
        success = initialize_finance_database(drop_existing=True)
        
        if not success:
            print("❌ Database initialization failed!")
            return False
            
        print("✅ Database initialized successfully!")
        
        # Create database connection
        db = create_finance_db()
        
        # Test inserting data with UUIDs
        print("\n🔄 Testing data insertion...")
        
        # Create a test user
        user = User(
            phone="+1987654321",
            name="Jane Smith", 
            email="jane.smith@example.com",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        
        # Prepare and insert user data
        user_data = UUIDHandler.prepare_for_mongodb(user.model_dump())
        result = db[MongoDBCollections.USERS].insert_one(user_data)
        print(f"✅ User inserted with MongoDB ID: {result.inserted_id}")
        print(f"✅ User UUID: {user.id}")
        
        # Create an account for the user
        account = Account(
            user_id=str(user.id),  # Convert UUID to string for foreign key
            account_type="checking",
            balance=1000.0,
            currency="USD",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        
        account_data = UUIDHandler.prepare_for_mongodb(account.model_dump())
        account_result = db[MongoDBCollections.ACCOUNTS].insert_one(account_data)
        print(f"✅ Account inserted with MongoDB ID: {account_result.inserted_id}")
        print(f"✅ Account UUID: {account.id}")
        
        # Test querying the data
        print("\n🔍 Testing data retrieval...")
        
        # Find user by UUID
        found_user = db[MongoDBCollections.USERS].find_one({"id": str(user.id)})
        if found_user:
            print(f"✅ Found user: {found_user['name']} with ID: {found_user['id']}")
        else:
            print("❌ User not found!")
            
        # Find accounts by user UUID
        user_accounts = list(db[MongoDBCollections.ACCOUNTS].find({"user_id": str(user.id)}))
        print(f"✅ Found {len(user_accounts)} accounts for user")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operation failed: {e}")
        import traceback
        print(f"📋 Full error: {traceback.format_exc()}")
        return False


def test_sample_data():
    """Test creating sample data with proper UUIDs."""
    print("\n📊 Testing Sample Data Creation")
    print("=" * 50)
    
    try:
        db = create_finance_db()
        initializer = MongoDBInitializer(db)
        
        # Create sample data
        success = initializer.create_sample_data()
        
        if success:
            print("✅ Sample data created successfully!")
            
            # Verify sample data
            verification = initializer.verify_setup()
            for collection, details in verification.items():
                print(f"📋 {collection}: {details['document_count']} documents")
        else:
            print("❌ Sample data creation failed!")
            
        return success
        
    except Exception as e:
        print(f"❌ Sample data test failed: {e}")
        return False


def main():
    """Run all UUID handling tests."""
    print("🚀 MongoDB UUID Handling Tests")
    print("=" * 60)
    
    # Test UUID handling functionality
    test_uuid_handling()
    
    # Test database operations
    db_success = test_database_operations()
    
    # Test sample data creation
    sample_success = test_sample_data()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 50)
    print(f"Database Operations: {'✅ PASSED' if db_success else '❌ FAILED'}")
    print(f"Sample Data Creation: {'✅ PASSED' if sample_success else '❌ FAILED'}")
    
    if db_success and sample_success:
        print("\n🎉 All tests passed! UUID handling is working correctly.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit(main())