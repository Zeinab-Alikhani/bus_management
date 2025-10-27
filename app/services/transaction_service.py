from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models.wallet import Wallet
from app.models.transaction import AppTransaction, TransactionType
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate

class TransactionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TransactionRepository(db)

    async def create_transaction(self, data: TransactionCreate):
        # 🔹 بررسی وجود کیف پول
        result = await self.db.execute(select(Wallet).where(Wallet.id == data.wallet_id))
        wallet = result.scalars().first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        # 🔹 تغییر موجودی بر اساس نوع تراکنش
        if data.type in [TransactionType.deposit, TransactionType.refund]:
            wallet.balance += data.amount
        elif data.type in [TransactionType.payment, TransactionType.adjustment]:
            if wallet.balance < data.amount:
                raise HTTPException(status_code=400, detail="Insufficient balance")
            wallet.balance -= data.amount

        wallet.updated_at = datetime.utcnow()

        # 🔹 ذخیره تراکنش
        transaction = AppTransaction(
            wallet_id=data.wallet_id,
            amount=data.amount,
            type=data.type,
            description=data.description,
        )
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def list_transactions(self, wallet_id: int):
        transactions = await self.repo.get_transactions_by_wallet(wallet_id)
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found")
        return transactions
