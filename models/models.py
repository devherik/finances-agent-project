"""Pydantic models for the application."""
from pydantic import BaseModel, Field
from enum import Enum

# Enums for various categorical fields
class TransactionType(str, Enum):
    EXPENSE = "expense"
    INCOME = "income"
    TRANSFER = "transfer"
    CREDIT = "credit"
    DEBIT = "debit"
    INVESTMENT = "investment"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"


# Transactions models and related entities
class User(BaseModel):
    id: str = Field(..., description="The unique identifier for the user")
    phone: str = Field(..., description="The phone number of the user")
    name: str = Field(..., description="The name of the user")
    email: str = Field(..., description="The email address of the user")
    created_at: str = Field(..., description="The timestamp when the user was created")
    updated_at: str = Field(..., description="The timestamp when the user was last updated")

class Account(BaseModel):
    id: str = Field(..., description="The unique identifier for the account")
    user_id: str = Field(..., description="The ID of the user who owns the account")
    account_type: str = Field(..., description="The type of the account (e.g., savings, checking)")
    balance: float = Field(..., description="The current balance of the account")
    currency: str = Field(..., description="The currency of the account")
    created_at: str = Field(..., description="The timestamp when the account was created")
    updated_at: str = Field(..., description="The timestamp when the account was last updated")
    
class TransactionCategory(BaseModel):
    id: str = Field(..., description="The unique identifier for the transaction category")
    name: str = Field(..., description="The name of the transaction category")
    description: str = Field(..., description="A brief description of the transaction category")
    created_at: str = Field(..., description="The timestamp when the category was created")
    updated_at: str = Field(..., description="The timestamp when the category was last updated")

class Transaction(BaseModel):
    id: str = Field(..., description="The unique identifier for the transaction")
    amount: float = Field(..., description="The amount of money involved in the transaction")
    currency: str = Field(..., description="The currency of the transaction")
    status: TransactionStatus = Field(..., description="The current status of the transaction")
    type: TransactionType = Field(..., description="The type of the transaction")
    date: str = Field(..., description="The date when the transaction occurred")
    created_at: str = Field(..., description="The timestamp when the transaction was created")
    updated_at: str = Field(..., description="The timestamp when the transaction was last updated")
    description: str = Field(..., description="A brief description of the transaction")
    category_id: str = Field(..., description="The ID of the category of the transaction (e.g., food, travel)")
    merchant: str = Field(..., description="The merchant associated with the transaction")
    account_id: str = Field(..., description="The account ID associated with the transaction")
    user_id: str = Field(..., description="The user ID associated with the transaction")