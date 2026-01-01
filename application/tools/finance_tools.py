from decimal import Decimal
from typing import Optional
from uuid import UUID

from agno.tools import Toolkit

from application.services.transaction_service import TransactionService
from application.services.account_service import AccountService
from domain.entities.transactions_entities import (
    TransactionCreate,
    TransactionType,
    TransactionStatus,
    AccountCreate,
    AccountUpdate,
)


class FinanceTools(Toolkit):
    def __init__(
        self,
        transaction_service: TransactionService,
        account_service: AccountService,
        user_id: UUID,
    ):
        super().__init__(name="finance_tools")
        self.transaction_service = transaction_service
        self.account_service = account_service
        self.user_id = user_id
        self.register(self.create_transaction)
        self.register(self.get_my_transactions)
        self.register(self.get_pending_incomes)
        self.register(self.create_account)
        self.register(self.get_my_accounts)
        self.register(self.get_account_balance)
        self.register(self.update_account_info)

    async def create_transaction(
        self,
        amount: Decimal,
        description: str,
        merchant: str,
        account_id: UUID,
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
            date_obj = datetime.datetime.now()
        else:
            try:
                date_obj = datetime.datetime.fromisoformat(date)
            except ValueError:
                date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")

        current_time = datetime.datetime.now()

        try:
            transaction_data = TransactionCreate(
                user_id=self.user_id,
                amount=amount,
                description=description,
                merchant=merchant,
                account_id=account_id,
                type=type,
                currency=currency,
                date=date_obj,
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
                user_id=self.user_id,
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

    async def get_my_transactions_by_text(self, text: str, limit: int = 5) -> str:
        """
        Retrieves the user's recent transactions based on a search text.

        Args:
            text: The search text to filter transactions.
            limit: The maximum number of transactions to return. Defaults to 5.

        Returns:
            A formatted string list of transactions matching the search text.
        """
        try:
            transactions = await self.transaction_service.get_transactions_by_text(
                user_id=self.user_id,
                text=text,
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

    async def get_balance_by_period(
        self, start_date: str, end_date: str, account_id: UUID
    ) -> str:
        """
        Retrieves the user's recent transactions based on a search text.

        Args:
            text: The search text to filter transactions.
            limit: The maximum number of transactions to return. Defaults to 5.

        Returns:
            A formatted string list of transactions matching the search text.
        """
        try:
            transactions = await self.transaction_service.get_balance_by_period(
                user_id=self.user_id,
                account_id=account_id,
                start_date=start_date,
                end_date=end_date,
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
                user_id=self.user_id
            )
            if not transactions:
                return "No pending incomes found."

            result = "Pending Incomes:\n"
            for t in transactions:
                result += f"- {t.date}: {t.description} ({t.merchant}) - {t.amount} {t.currency}\n"
            return result
        except Exception as e:
            return f"Failed to fetch pending incomes: {str(e)}"

    async def create_account(
        self,
        name: str,
        account_type: str,
        balance: float,
        currency: str = "USD",
    ) -> str:
        """
        Creates a new financial account (e.g., checking, savings).

        Args:
            account_type: The type of account (e.g., 'checking', 'savings', 'investment').
            balance: Initial balance. Must be positive.
            currency: Currency code (e.g., 'USD'). Defaults to 'USD'.

        Returns:
            Confirmation message with account ID.
        """
        import datetime

        current_time = datetime.datetime.now()
        try:
            account_data = AccountCreate(
                user_id=self.user_id,
                name=name,
                account_type=account_type,
                balance=Decimal(str(balance)),
                currency=currency,
                created_at=current_time,
                updated_at=current_time,
            )
            result = await self.account_service.create_account(account_data)
            return f"Account created successfully. ID: {result.id}"
        except Exception as e:
            return f"Failed to create account: {str(e)}"

    async def get_my_accounts(self) -> str:
        """
        Retrieves the user's accounts.

        Returns:
            A formatted string list of accounts.
        """
        try:
            accounts = await self.account_service.get_user_accounts(
                user_id=self.user_id
            )
            if not accounts:
                return "No accounts found."

            result = "Your Accounts:\n"
            for acc in accounts:
                result += f"- {acc.account_type.capitalize()}: {acc.balance} {acc.currency} (ID: {acc.id}, NAME: {acc.name})\n"
            return result
        except Exception as e:
            return f"Failed to fetch accounts: {str(e)}"

    async def get_account_balance(self, account_id: UUID) -> str:
        """
        Gets the balance of a specific account.

        Args:
            account_id: The ID of the account.

        Returns:
            The balance or error message.
        """
        try:
            balance = await self.account_service.get_account_balance(
                user_id=self.user_id,
                account_id=account_id,
            )
            if balance is None:
                return "Account not found or access denied."
            return f"Current Balance: {balance}"
        except Exception as e:
            return f"Failed to fetch balance: {str(e)}"

    async def update_account_info(
        self,
        account_id: UUID,
        account_type: Optional[str] = None,
        currency: Optional[str] = None,
    ) -> str:
        """
        Updates account information.

        Args:
            account_id: The ID of the account to update.
            account_type: New account type (optional).
            currency: New currency (optional).

        Returns:
            Confirmation message or error.
        """
        import datetime

        try:
            # Fetch existing account
            account = await self.account_service.get_account(account_id)
            if not account or str(account.user_id) != str(self.user_id):
                return "Account not found or access denied."

            # Update fields
            updated_data = account.model_dump()
            if account_type:
                updated_data["account_type"] = account_type
            if currency:
                updated_data["currency"] = currency

            updated_data["updated_at"] = datetime.datetime.now()

            # Create update object
            update_obj = AccountUpdate(**updated_data)

            result = await self.account_service.update_account(account_id, update_obj)
            if result:
                return "Account updated successfully."
            return "Failed to update account."
        except Exception as e:
            return f"Error updating account: {str(e)}"
