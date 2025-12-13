from enum import Enum


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
