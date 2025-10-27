from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.wallet import Wallet

class WalletRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ✅ ایجاد کیف پول جدید
    async def create_wallet(self, wallet: Wallet) -> Wallet:
        self.db.add(wallet)
        await self.db.commit()
        await self.db.refresh(wallet)
        return wallet

    # ✅ گرفتن کیف پول با شناسه کاربر
    async def get_wallet_by_user_id(self, user_id: int) -> Wallet | None:
        result = await self.db.execute(select(Wallet).where(Wallet.user_id == user_id))
        return result.scalars().first()

    # ✅ به‌روزرسانی موجودی (افزایش/کاهش)
    async def update_wallet_balance(self, user_id: int, amount: float) -> Wallet | None:
        result = await self.db.execute(select(Wallet).where(Wallet.user_id == user_id))
        wallet = result.scalars().first()
        if not wallet:
            return None

        wallet.balance += amount
        await self.db.commit()
        await self.db.refresh(wallet)
        return wallet

    # ✅ حذف کیف پول (در صورت نیاز)
    async def delete_wallet(self, user_id: int) -> bool:
        wallet = await self.get_wallet_by_user_id(user_id)
        if wallet:
            await self.db.delete(wallet)
            await self.db.commit()
            return True
        return False
