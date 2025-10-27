from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.transaction import AppTransaction, TransactionType

class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ✅ ایجاد تراکنش جدید (هماهنگ با BookingService)
    async def create_transaction(self, wallet_id: int, amount: float, transaction_type: TransactionType, description: str = None):
        transaction = AppTransaction(
            wallet_id=wallet_id,
            amount=amount,
             transaction_type=transaction_type,
            description=description
        )
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    # ✅ دریافت تمام تراکنش‌های یک کیف پول
    async def get_transactions_by_wallet(self, wallet_id: int):
        result = await self.db.execute(select(AppTransaction).where(AppTransaction.wallet_id == wallet_id))
        return result.scalars().all()
