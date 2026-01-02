from decimal import Decimal
from typing import Optional, Any
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
        self.register(self.get_balance_by_period)
        self.register(self.get_my_transactions_by_text)
        self.register(self.create_account)
        self.register(self.get_my_accounts)
        self.register(self.get_account_balance)
        self.register(self.update_account_info)
        self.register(self.delete_my_account)

    def _parse_uuid(self, value: Any) -> UUID:
        """
        Robustly parses a UUID from various input formats.
        Handles raw UUID objects, strings, and dictionaries common in LLM hallucinations.
        """
        if isinstance(value, UUID):
            return value

        if isinstance(value, str):
            try:
                return UUID(value)
            except ValueError:
                pass

        if isinstance(value, dict):
            # Check for common ID keys in LLM structures
            for key in ["id", "account_id", "uuid", "value"]:
                if key in value:
                    return self._parse_uuid(value[key])

        raise ValueError(
            f"Invalid UUID format: {value}. Expected UUID string or dict with 'id' key."
        )

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
        Records a new financial transaction (expense or income) for the authenticated user.
        Use this tool whenever the user reports spending money, buying an item/service, or receiving funds.

        Args:
            amount (Decimal): The numeric value of the transaction. Must be a positive value.
                Example: 45.50
            description (str): A descriptive name for the transaction that helps identify it later.
                Example: "Grocery shopping", "Freelance Payment"
            merchant (str): The entity involved in the transaction (store name or payer).
                Example: "Walmart", "Client ABC"
            account_id (UUID): The unique ID of the financial account to be debited (for expenses)
                or credited (for income). Use 'get_my_accounts' to find valid account IDs.
            type (TransactionType, optional): Specifies if it's an 'EXPENSE' or 'INCOME'.
                Defaults to TransactionType.EXPENSE.
            currency (str, optional): The 3-letter ISO currency code. Defaults to 'USD'.
            date (str, optional): The transaction date in ISO 8601 format (YYYY-MM-DD).
                If omitted, the system defaults to the current date. Example: "2023-12-25"

        Returns:
            str: A confirmation message containing the newly created transaction's ID or an error message.
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
            parsed_account_id = self._parse_uuid(account_id)
            transaction_data = TransactionCreate(
                user_id=self.user_id,
                amount=amount,
                description=description,
                merchant=merchant,
                account_id=parsed_account_id,
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
        Fetches a list of the user's most recent financial transactions.
        Use this to give the user an overview of their latest spending or income activity.

        Args:
            limit (int, optional): The maximum number of transactions to retrieve.
                Best used to avoid overwhelming the user with too much data. Defaults to 5.

        Returns:
            str: A human-readable formatted list of transactions including date, description,
                merchant, amount, currency, and type.
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
        Searches for transactions using a specific text keyword or phrase.
        Use this when the user asks about specific purchases (e.g., "Show me my transactions at Amazon")
        or categories (e.g., "Find all grocery transactions").

        Args:
            text (str): The keyword, merchant name, or description piece to search for.
            limit (int, optional): Maximum number of matching transactions to return. Defaults to 5.

        Returns:
            str: A formatted list of matching transactions or a message indicating none were found.
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
        Calculates or summarizes transactions for a specific account within a given date range.
        Use this to answer questions about spending or income over a specific month, week, or year.

        Args:
            start_date (str): The beginning of the period in 'YYYY-MM-DD' format.
            end_date (str): The end of the period in 'YYYY-MM-DD' format.
            account_id (UUID): The ID of the account to analyze.

        Returns:
            str: A formatted list of transactions found within the period for that account.
        """
        try:
            parsed_account_id = self._parse_uuid(account_id)
            transactions = await self.transaction_service.get_balance_by_period(
                user_id=self.user_id,
                account_id=parsed_account_id,
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
        Retrieves income entries that have been recorded but might not yet be fully processed or cleared.
        Use this when the user asks about expected payments or upcoming income.

        Returns:
             str: A formatted list of pending income transactions.
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
        Creates a new financial account for the user to track balances and transactions.
        Use this when the user wants to start tracking a new bank account, credit card, or cash wallet.

        Args:
            name (str): A user-defined name for the account (e.g., "Personal Checking", "Business Visa").
            account_type (str): The category of the account (e.g., 'checking', 'savings', 'credit_card', 'investment').
            balance (float): The initial opening balance of the account. Must be provided as a float.
            currency (str, optional): The 3-letter ISO currency code. Defaults to 'USD'.

        Returns:
            str: A success message with the new account UUID or an error message.
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
        Lists all financial accounts owned by the current user.
        Crucial for obtaining account_ids required by other tools like 'create_transaction' or 'get_account_balance'.

        Returns:
            str: A formatted list showing account type, balance, currency, ID, and Name for each account.
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
        Provides the current available balance for a specific account.
        Use this tool when the user asks "How much money do I have in my savings?" or "What's my balance?".

        Args:
            account_id (UUID): The unique identifier of the account. Obtain this from 'get_my_accounts'.

        Returns:
            str: The current balance formatted with the currency, or an error/not found message.
        """
        try:
            parsed_account_id = self._parse_uuid(account_id)
            balance = await self.account_service.get_account_balance(
                user_id=self.user_id,
                account_id=parsed_account_id,
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
        Modifies the properties of an existing financial account.
        Use this when the user wants to change an account's category or default currency.

        Args:
            account_id (UUID): The ID of the account to be updated.
            account_type (Optional[str], optional): The new category for the account (e.g., 'savings').
            currency (Optional[str], optional): The new 3-letter currency code (e.g., 'EUR').

        Returns:
            str: A confirmation of the update or an error message.
        """
        import datetime

        try:
            parsed_account_id = self._parse_uuid(account_id)
            # Fetch existing account
            account = await self.account_service.get_account(parsed_account_id)
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

            result = await self.account_service.update_account(
                parsed_account_id, update_obj
            )
            if result:
                return "Account updated successfully."
            return "Failed to update account."
        except Exception as e:
            return f"Error updating account: {str(e)}"

    async def delete_my_account(
        self,
        account_id: UUID,
    ) -> str:
        """
        Permanently removes a financial account from the user's profile.
        WARNING: This action is destructive. Use only when the user explicitly requests to delete an account.

        Args:
            account_id (UUID): The ID of the account to delete.

        Returns:
            str: A confirmation message of deletion or an error message.
        """
        try:
            parsed_account_id = self._parse_uuid(account_id)
            # Fetch existing account
            account = await self.account_service.get_account(parsed_account_id)
            if not account or str(account.user_id) != str(self.user_id):
                return "Account not found or access denied."

            result = await self.account_service.delete_account(parsed_account_id)
            if result:
                return "Account deleted successfully."
            return "Failed to delete account."
        except Exception as e:
            return f"Error deleting account: {str(e)}"
