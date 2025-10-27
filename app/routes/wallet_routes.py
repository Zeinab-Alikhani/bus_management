from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import AsyncSessionLocal
from app.schemas.wallet import WalletCreate, WalletRead, WalletUpdate
from app.services.wallet_service import WalletService
from app.models.user import User
from app.utils.auth_utils import get_current_user
from app.core.security import oauth2_scheme

router = APIRouter(prefix="/api/wallets", tags=["Wallets"])

# Dependency: اتصال به دیتابیس
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# 🟢 ایجاد کیف پول برای کاربر لاگین‌شده
#@router.post("/", response_model=WalletRead)
#async def create_wallet(
    #data: WalletCreate,
   # db: AsyncSession = Depends(get_db),
    #current_user: User = Depends(get_current_user)  # 👈 مستقیم از JWT
#):
    #service = WalletService(db)
    #return await service.create_wallet(current_user.id, data)  # ✅ user_id از JWT


# 🟢 فقط کاربر لاگین کرده کیف پول خودش را می‌بیند
@router.get("/", response_model=WalletRead)
async def get_my_wallet(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = WalletService(db)
    return await service.get_wallet(current_user.id)  # ✅ متد درست در Service


# 🟢 فقط خودش می‌تونه کیف پولش را آپدیت کنه
@router.put("/", response_model=WalletRead)
async def update_my_wallet(
    data: WalletUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = WalletService(db)
    return await service.update_wallet_balance(current_user.id, data)


# 🔹 واریز وجه (شارژ کیف پول)
@router.post("/deposit")
async def deposit(
    amount: float,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = WalletService(db)
    return await service.deposit(current_user.id, amount)


# 🔹 برداشت وجه
@router.post("/withdraw")
async def withdraw(
    amount: float,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = WalletService(db)
    return await service.withdraw(current_user.id, amount)
