from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.db import AsyncSessionLocal
from app.schemas.booking import BookingCreate, BookingRead, BookingUpdate
from app.services.booking_service import BookingService
from app.models.user import User
from app.utils.auth_utils import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# 🟢 ایجاد رزرو
@router.post("/", response_model=dict)
async def create_booking(
    data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    service = BookingService(db)
    return await service.create_booking(data, current_user) 


# 🟢 دیدن رزروهای کاربر فعلی
@router.get("/my", response_model=List[BookingRead])
async def list_my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = BookingService(db)
    return await service.get_bookings_by_user(current_user.id)


# 🔹 لغو رزرو
@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = BookingService(db)
    booking = await service.get_booking(booking_id)
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return await service.cancel_booking(booking_id)
