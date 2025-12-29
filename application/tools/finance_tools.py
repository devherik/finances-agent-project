from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from agno.agent import Agent
from agno.tools import Toolkit

from application.services.transaction_service import TransactionService
from domain.entities.transactions_entities import (
    TransactionCreate,
    TransactionType,
    TransactionStatus,
)
from domain.entities.user_entities import UserBase


class FinanceTools(Toolkit):
    def __init__(
        self,
        transaction_service: TransactionService,
        user_id: str,
    ):
        super().__init__(name="finance_tools")
        self.transaction_service = transaction_service
        self.user_id = user_id
        self.register(self.create_transaction)
        self.register(self.get_my_transactions)
        self.register(self.get_pending_incomes)

    async def create_transaction(
        self,
        amount: Decimal,
        description: str,
        merchant: str,
        account_id: str,
        type: TransactionType = TransactionType.EXPENSE,
        currency: str = "USD",
        date: str = "",  # optional, default to now if empty
    ) -> str:
        """
        Records a new financial transaction (expense or income).
        Use this when the user mentions buying something, spending money, or receiving income.

        Args:
            amount: The amount of the transaction. Must be positive.
            description: A brief description of what was purchased or the income source.
            merchant: The name of the merchant or payer.
            account_id: The ID of the account to charge/credit.
            type: The type of transaction (EXPENSE or INCOME). Defaults to EXPENSE.
            currency: The 3-letter currency code (e.g., 'USD', 'BRL'). Defaults to 'USD'.
            date: The date of the transaction in ISO 8601 format (YYYY-MM-DD). If not provided, current date is used.

        Returns:
            A confirmation message with the transaction ID.
        """
        import datetime

        if not date:
            date = datetime.date.today().isoformat()

        current_time = datetime.datetime.now().isoformat()

        try:
            transaction_data = TransactionCreate(
                user_id=self.user_id,
                amount=amount,
                description=description,
                merchant=merchant,
                account_id=account_id,
                type=type,
                currency=currency,
                date=date,
                status=TransactionStatus.COMPLETED,
                created_at=current_time,
                updated_at=current_time,
            )

            result = await self.transaction_service.create_transaction(transaction_data)
            return f"Transaction recorded successfully. ID: {result.id}"
        except Exception as e:
            return f"Failed to create transaction: {str(e)}"

    async def get_my_transactions(self, limit: int = 5) -> str:
        """
        Retrieves the user's recent transactions.

        Args:
            limit: The maximum number of transactions to return. Defaults to 5.

        Returns:
            A formatted string list of transactions.
        """
        try:
            transactions = await self.transaction_service.get_user_transactions(
                user_id=UUID(self.user_id)
                if isinstance(self.user_id, str)
                else self.user_id,
                limit=limit,
            )
            if not transactions:
                return "No recent transactions found."

            result = "Recent Transactions:\n"
            for t in transactions:
                result += f"- {t.date}: {t.description} ({t.merchant}) - {t.amount} {t.currency} [{t.type.value}]\n"
            return result
        except Exception as e:
            return f"Failed to fetch transactions: {str(e)}"

    async def get_pending_incomes(self) -> str:
        """
        Retrieves all pending income transactions.

        Returns:
             A formatted string list of pending incomes.
        """
        try:
            transactions = await self.transaction_service.get_pending_incomes(
                user_id=UUID(self.user_id)
                if isinstance(self.user_id, str)
                else self.user_id
            )
            if not transactions:
                return "No pending incomes found."

            result = "Pending Incomes:\n"
            for t in transactions:
                result += f"- {t.date}: {t.description} ({t.merchant}) - {t.amount} {t.currency}\n"
            return result
        except Exception as e:
            return f"Failed to fetch pending incomes: {str(e)}"
