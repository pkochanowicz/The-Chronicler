import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.db_schemas import (
    Item,
    GuildBankItem,
    GuildBankTransaction,
    BankTransactionTypeEnum,
)

logger = logging.getLogger(__name__)


class GuildBankService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def deposit_item(
        self,
        user_id: int,
        item_name: str,
        quantity: int,
        category: str = "General",
        notes: str = None,
    ) -> bool:
        """
        Deposits an item into the guild bank.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")

        # 1. Find the Item
        stmt = select(Item).where(Item.name == item_name)
        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()

        if not item:
            logger.error(f"Item '{item_name}' not found in database.")
            raise ValueError(
                f"Item '{item_name}' does not exist in the database. Please request an item addition first."
            )

        # 2. Find or Create Bank Entry
        stmt_bank = select(GuildBankItem).where(GuildBankItem.item_id == item.id)
        result_bank = await self.session.execute(stmt_bank)
        bank_item = result_bank.scalar_one_or_none()

        if bank_item:
            bank_item.count += quantity
            if category != "General":
                bank_item.category = category
        else:
            bank_item = GuildBankItem(
                item_id=item.id, count=quantity, category=category
            )
            self.session.add(bank_item)

        # 3. Log Transaction
        transaction = GuildBankTransaction(
            item_id=item.id,
            user_id=user_id,
            transaction_type=BankTransactionTypeEnum.DEPOSIT,
            quantity=quantity,
            notes=notes,
        )
        self.session.add(transaction)

        await self.session.commit()
        logger.info(f"User {user_id} deposited {quantity}x {item_name}.")
        return True

    async def withdraw_item(
        self, user_id: int, item_id: int, quantity: int, notes: str = None
    ) -> bool:
        """
        Withdraws an item from the guild bank.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")

        # 1. Find Bank Entry
        stmt = select(GuildBankItem).where(GuildBankItem.item_id == item_id)
        result = await self.session.execute(stmt)
        bank_item = result.scalar_one_or_none()

        if not bank_item:
            raise ValueError(f"Item ID {item_id} not found in the bank.")

        if bank_item.count < quantity:
            raise ValueError(
                f"Insufficient quantity. Requested: {quantity}, Available: {bank_item.count}"
            )

        # 2. Update Count
        bank_item.count -= quantity

        # 3. Log Transaction
        transaction = GuildBankTransaction(
            item_id=item_id,
            user_id=user_id,
            transaction_type=BankTransactionTypeEnum.WITHDRAWAL,
            quantity=quantity,
            notes=notes,
        )
        self.session.add(transaction)

        await self.session.commit()
        logger.info(f"User {user_id} withdrawn {quantity}x Item {item_id}.")
        return True

    async def get_all_items(self):
        """Returns all items in the bank with count > 0."""
        stmt = (
            select(GuildBankItem, Item)
            .join(Item)
            .where(GuildBankItem.count > 0)
            .order_by(GuildBankItem.category, Item.name)
        )
        result = await self.session.execute(stmt)
        return result.all()  # Returns list of (GuildBankItem, Item) tuples

    async def get_member_deposits(self, user_id: int, limit: int = 20):
        """Returns recent deposits by a member."""
        stmt = (
            select(GuildBankTransaction, Item)
            .join(Item)
            .where(
                GuildBankTransaction.user_id == user_id,
                GuildBankTransaction.transaction_type
                == BankTransactionTypeEnum.DEPOSIT,
            )
            .order_by(GuildBankTransaction.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.all()  # Returns list of (GuildBankTransaction, Item) tuples
