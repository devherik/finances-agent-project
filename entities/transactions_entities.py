from pydantic import BaseModel, Field, field_validator
from uuid import UUID, uuid4
from decimal import Decimal

from .enuns import TransactionType, TransactionStatus


# Base Entities
class AccountBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="The unique identifier for the account",
        alias="_id",
    )
    user_id: str = Field(..., description="The ID of the user who owns the account")
    account_type: str = Field(
        ..., description="The type of the account (e.g., savings, checking)"
    )
    balance: Decimal = Field(..., description="The current balance of the account")
    currency: str = Field(..., description="The currency of the account")
    created_at: str = Field(
        ..., description="The timestamp when the account was created"
    )
    updated_at: str = Field(
        ..., description="The timestamp when the account was last updated"
    )

    class Config:
        from_attributes = True
        populate_by_name = True


class TransactionBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="The unique identifier for the transaction",
        alias="_id",
    )
    user_id: str = Field(..., description="The ID of the user who owns the transaction")
    amount: Decimal = Field(
        ..., description="The amount of money involved in the transaction"
    )
    currency: str = Field(..., description="The currency of the transaction")
    status: TransactionStatus = Field(
        ..., description="The current status of the transaction"
    )
    type: TransactionType = Field(..., description="The type of the transaction")
    date: str = Field(..., description="The date when the transaction occurred")
    created_at: str = Field(
        ..., description="The timestamp when the transaction was created"
    )
    updated_at: str = Field(
        ..., description="The timestamp when the transaction was last updated"
    )
    description: str = Field(..., description="A brief description of the transaction")
    category_id: str = Field(
        ...,
        description="The ID of the category of the transaction (e.g., food, travel)",
    )
    merchant: str = Field(
        ..., description="The merchant associated with the transaction"
    )
    account_id: str = Field(
        ..., description="The account ID associated with the transaction"
    )
    user_id: str = Field(..., description="The user ID associated with the transaction")

    @field_validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @field_validator("currency")
    def currency_must_be_valid(cls, v):
        if len(v) != 3:
            raise ValueError("Currency must be a 3-letter ISO code")
        return v.upper()

    @field_validator("date", "created_at", "updated_at")
    def date_must_be_iso_format(cls, v):
        # Simple check for ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)
        if not isinstance(v, str) or len(v) < 10 or v[4] != "-" or v[7] != "-":
            raise ValueError("Date must be in ISO 8601 format")
        return v

    @field_validator("status")
    def status_must_be_valid(cls, v):
        if v not in TransactionStatus:
            raise ValueError(f"Status must be one of {list(TransactionStatus)}")
        return v

    @field_validator("type")
    def type_must_be_valid(cls, v):
        if v not in TransactionType:
            raise ValueError(f"Type must be one of {list(TransactionType)}")
        return v

    class Config:
        from_attributes = True
        populate_by_name = True


# Data Transfer Objects
class AccountCreate(AccountBase):
    user_id: str = Field(..., description="The ID of the user who owns the account")
    account_type: str = Field(
        ..., description="The type of the account (e.g., savings, checking)"
    )
    balance: Decimal = Field(..., description="The current balance of the account")
    currency: str = Field(..., description="The currency of the account")

    @field_validator("balance")
    def balance_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Balance must be positive")
        return v

    @field_validator("currency")
    def currency_must_be_valid(cls, v):
        if len(v) != 3:
            raise ValueError("Currency must be a 3-letter ISO code")
        return v.upper()


class AccountUpdate(AccountBase):
    user_id: str = Field(..., description="The ID of the user who owns the account")
    account_type: str = Field(
        ..., description="The type of the account (e.g., savings, checking)"
    )
    balance: Decimal = Field(..., description="The current balance of the account")
    currency: str = Field(..., description="The currency of the account")

    @field_validator("balance")
    def balance_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Balance must be positive")
        return v

    @field_validator("currency")
    def currency_must_be_valid(cls, v):
        if len(v) != 3:
            raise ValueError("Currency must be a 3-letter ISO code")
        return v.upper()


class AccountDelete(AccountBase):
    user_id: str = Field(..., description="The ID of the user who owns the account")


class TransactionCreate(TransactionBase):
    user_id: str = Field(..., description="The ID of the user who owns the transaction")
    amount: Decimal = Field(
        ..., description="The amount of money involved in the transaction"
    )
    currency: str = Field(..., description="The currency of the transaction")
    status: TransactionStatus = Field(
        ..., description="The current status of the transaction"
    )
    type: TransactionType = Field(..., description="The type of the transaction")
    date: str = Field(..., description="The date when the transaction occurred")
    created_at: str = Field(
        ..., description="The timestamp when the transaction was created"
    )
    updated_at: str = Field(
        ..., description="The timestamp when the transaction was last updated"
    )
    description: str = Field(..., description="A brief description of the transaction")
    category_id: str = Field(
        ...,
        description="The ID of the category of the transaction (e.g., food, travel)",
    )
    merchant: str = Field(
        ..., description="The merchant associated with the transaction"
    )
    account_id: str = Field(
        ..., description="The account ID associated with the transaction"
    )


class TransactionUpdate(TransactionBase):
    user_id: str = Field(..., description="The ID of the user who owns the transaction")
    amount: Decimal = Field(
        ..., description="The amount of money involved in the transaction"
    )
    currency: str = Field(..., description="The currency of the transaction")
    status: TransactionStatus = Field(
        ..., description="The current status of the transaction"
    )
    type: TransactionType = Field(..., description="The type of the transaction")
    date: str = Field(..., description="The date when the transaction occurred")
    created_at: str = Field(
        ..., description="The timestamp when the transaction was created"
    )
    updated_at: str = Field(
        ..., description="The timestamp when the transaction was last updated"
    )
    description: str = Field(..., description="A brief description of the transaction")
    category_id: str = Field(
        ...,
        description="The ID of the category of the transaction (e.g., food, travel)",
    )
    merchant: str = Field(
        ..., description="The merchant associated with the transaction"
    )
    account_id: str = Field(
        ..., description="The account ID associated with the transaction"
    )


class TransactionDelete(TransactionBase):
    user_id: str = Field(..., description="The ID of the user who owns the transaction")
