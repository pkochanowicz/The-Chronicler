import pytest
from sqlalchemy import select
from services.bank_service import GuildBankService
from schemas.db_schemas import (
    Item,
    GuildBankItem,
    GuildBankTransaction,
    BankTransactionTypeEnum,
    ItemQualityEnum,
)


@pytest.fixture
def bank_service(async_session):
    return GuildBankService(async_session)


@pytest.mark.asyncio
async def test_deposit_item_success(bank_service, async_session):
    # 1. Setup: Create a valid Item in the DB
    test_item = Item(
        id=12345,
        name="Thunderfury, Blessed Blade of the Windseeker",
        turtle_db_url="http://fake.url",
        icon_url="http://fake.icon",
        quality=ItemQualityEnum.Legendary,
        item_type="Weapon",
    )
    async_session.add(test_item)
    await async_session.commit()

    # 2. Action: Deposit
    result = await bank_service.deposit_item(
        user_id=112233,
        item_name="Thunderfury, Blessed Blade of the Windseeker",
        quantity=1,
        category="Legendaries",
    )

    # 3. Verification
    assert result is True

    # Check Inventory
    stmt = select(GuildBankItem).where(GuildBankItem.item_id == 12345)
    bank_item = (await async_session.execute(stmt)).scalar_one_or_none()
    assert bank_item is not None
    assert bank_item.count == 1
    assert bank_item.category == "Legendaries"

    # Check Transaction Log
    stmt_tx = select(GuildBankTransaction).where(GuildBankTransaction.item_id == 12345)
    transaction = (await async_session.execute(stmt_tx)).scalar_one_or_none()
    assert transaction is not None
    assert transaction.user_id == 112233
    assert transaction.quantity == 1
    assert transaction.transaction_type == BankTransactionTypeEnum.DEPOSIT


@pytest.mark.asyncio
async def test_withdraw_item_success(bank_service, async_session):
    # 1. Setup: Create Item and existing Stock
    test_item = Item(
        id=999,
        name="Linen Cloth",
        turtle_db_url="http://fake.url",
        icon_url="http://fake.icon",
        quality=ItemQualityEnum.Common,
        item_type="Trade Goods",
    )
    async_session.add(test_item)
    await async_session.commit()

    # Add initial stock directly
    initial_stock = GuildBankItem(item_id=999, count=20, category="Materials")
    async_session.add(initial_stock)
    await async_session.commit()

    # 2. Action: Withdraw
    result = await bank_service.withdraw_item(user_id=445566, item_id=999, quantity=5)

    # 3. Verification
    assert result is True

    # Check Inventory Decreased
    await async_session.refresh(initial_stock)
    assert initial_stock.count == 15

    # Check Transaction Log
    stmt_tx = select(GuildBankTransaction).where(
        GuildBankTransaction.item_id == 999,
        GuildBankTransaction.transaction_type == BankTransactionTypeEnum.WITHDRAWAL,
    )
    transaction = (await async_session.execute(stmt_tx)).scalar_one_or_none()
    assert transaction is not None
    assert transaction.user_id == 445566
    assert transaction.quantity == 5


@pytest.mark.asyncio
async def test_withdraw_insufficient_funds(bank_service, async_session):
    # 1. Setup: Create Item and existing Stock
    test_item = Item(
        id=555,
        name="Gold Bar",
        turtle_db_url="http://fake.url",
        icon_url="http://fake.icon",
        quality=ItemQualityEnum.Uncommon,
        item_type="Trade Goods",
    )
    async_session.add(test_item)

    stock = GuildBankItem(item_id=555, count=2, category="Materials")
    async_session.add(stock)
    await async_session.commit()

    # 2. Action: Try to withdraw more than exists
    with pytest.raises(ValueError, match="Insufficient quantity"):
        await bank_service.withdraw_item(user_id=777, item_id=555, quantity=10)

    # 3. Verify stock unchanged
    await async_session.refresh(stock)
    assert stock.count == 2
