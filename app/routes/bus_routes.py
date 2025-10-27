from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.utils.auth_utils import get_current_user, require_role
from app.core.db import AsyncSessionLocal
from app.schemas.bus import BusCreate, BusUpdate, BusResponse
from app.services.bus_service import BusService


router = APIRouter(prefix="/buses", tags=["Buses"])

# تابع وابستگی برای گرفتن session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# 🟢 فقط ادمین می‌تونه اتوبوس جدید ثبت کنه
@router.post("/", response_model=BusResponse, status_code=status.HTTP_201_CREATED, description=" فقط ادمین می‌تواند اتوبوس جدید اضافه کند.")
@require_role("admin") 
async def create_bus(
    data: BusCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # بررسی نقش ادمین
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create buses")

    service = BusService(db)
    return await service.create_bus(data)


# 🟡 دریافت همه‌ی اتوبوس‌ها (در دسترس همه کاربران)
@router.get("/", response_model=List[BusResponse])
async def get_all_buses(db: AsyncSession = Depends(get_db)):
    service = BusService(db)
    return await service.get_all_buses()


# 🔵 دریافت جزئیات یک اتوبوس خاص
@router.get("/{bus_id}", response_model=BusResponse)
async def get_bus(bus_id: int, db: AsyncSession = Depends(get_db)):
    service = BusService(db)
    return await service.get_bus_by_id(bus_id)


# 🟣 به‌روزرسانی اطلاعات اتوبوس — فقط توسط ادمین
@router.put("/{bus_id}", response_model=BusResponse)
async def update_bus(
    bus_id: int,
    data: BusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update buses")

    service = BusService(db)
    return await service.update_bus(bus_id, data)


# 🔴 حذف اتوبوس — فقط ادمین
@router.delete("/{bus_id}", status_code=status.HTTP_200_OK)
async def delete_bus(
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete buses")

    service = BusService(db)
    return await service.delete_bus(bus_id)
