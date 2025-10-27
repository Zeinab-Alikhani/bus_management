from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import AsyncSessionLocal
from app.schemas.user import UserCreate, UserRead, UserResponse, UserUpdate
from app.services.user_service import UserService
from typing import List
from app.models.user import User
from app.utils.auth_utils import get_current_user
from app.core.security import oauth2_scheme  # 👈 اضافه شد

router = APIRouter()

# Dependency برای گرفتن سشن دیتابیس
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# 🟢 ثبت‌نام کاربر جدید (عمومی)
@router.post("/", response_model=UserRead)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.register_user(data)


# 🔐 دریافت اطلاعات کاربر (فقط برای کاربر لاگین‌شده یا ادمین)
@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),  # 👈 اضافه شد
):
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# 🔐 لیست تمام کاربران (مثلاً فقط برای ادمین)
@router.get("/", response_model=List[UserRead])
async def list_users(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),  # 👈 اضافه شد
):
    service = UserService(db)
    return await service.list_users()


# 🔐 بروزرسانی اطلاعات کاربر (فقط خودش یا ادمین)
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),  # 👈 اضافه شد
):
    service = UserService(db)
    return await service.update_user(user_id, data)


# 🔐 حذف کاربر (فقط ادمین یا خودش)
@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),  # 👈 اضافه شد
):
    service = UserService(db)
    return await service.delete_user(user_id)
