from decimal import Decimal
from fastapi import HTTPException
from app.models.transaction import TransactionType
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.wallet_repository import WalletRepository


class WalletService:
    def __init__(self, db):
        self.db = db
        self.repo = WalletRepository(db)
        self.transaction_repo = TransactionRepository(db)


    async def get_wallet(self, user_id: int):
        wallet = await self.repo.get_wallet_by_user_id(user_id)
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        return wallet
    

    # 🟢 واریز وجه
    async def deposit(self, user_id: int, amount: float):
        wallet = await self.repo.get_wallet_by_user_id(user_id)
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        # 👇 تبدیل float به Decimal قبل از جمع
        wallet.balance += Decimal(str(amount))
        await self.db.commit()
        await self.db.refresh(wallet)

        await self.transaction_repo.create_transaction(
            wallet_id=wallet.id,
            amount=Decimal(str(amount)),
            transaction_type=TransactionType.deposit,
            description=f"Deposit of {amount} units"
        )

        return {
            "message": "Deposit successful",
            "new_balance": float(wallet.balance)
        }

    # 🔻 برداشت وجه
    async def withdraw(self, user_id: int, amount: float):
        wallet = await self.repo.get_wallet_by_user_id(user_id)
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        if wallet.balance < Decimal(str(amount)):
            raise HTTPException(status_code=400, detail="Insufficient balance")

        wallet.balance -= Decimal(str(amount))
        await self.db.commit()
        await self.db.refresh(wallet)

        await self.transaction_repo.create_transaction(
            wallet_id=wallet.id,
            amount=-Decimal(str(amount)),
            transaction_type=TransactionType.withdraw,
            description=f"Withdraw of {amount} units"
        )

        return {
            "message": "Withdraw successful",
            "new_balance": float(wallet.balance)
        }
