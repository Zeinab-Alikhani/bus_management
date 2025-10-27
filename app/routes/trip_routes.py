from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.core.db import AsyncSessionLocal
from app.schemas.trip import TripCreate, TripResponse, TripUpdate, TripRead
from app.services.trip_service import TripService
from app.utils.auth_utils import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/trips", tags=["Trips"])

# 🧱 Session dependency
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


# 🟢 ایجاد سفر جدید — فقط ادمین
@router.post(
    "/",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
    summary="🛫 ایجاد سفر جدید (فقط ادمین)",
    description="تنها **ادمین** می‌تواند سفر جدید ایجاد کند. سایر کاربران با خطای 403 روبرو می‌شوند."
)
@require_role("admin")
async def create_trip(
    data: TripCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = TripService(db)
    return await service.create_trip(data)


# 🟡 لیست تمام سفرها — در دسترس همه کاربران
@router.get(
    "/",
    response_model=List[TripResponse],
    summary="📋 لیست تمام سفرها",
    description="تمام کاربران (ادمین، راننده، اپراتور، مسافر) می‌توانند لیست سفرها را ببینند."
)
async def list_trips(db: AsyncSession = Depends(get_db)):
    service = TripService(db)
    return await service.list_trips()


# 🔍 جستجوی سفرها — عمومی
@router.get(
    "/search",
    response_model=List[TripRead],
    summary="🔎 جستجوی سفرها",
    description="کاربران می‌توانند بر اساس مبدا، مقصد و قیمت سفرها را جستجو کنند."
)
async def search_trips(
    origin: Optional[str] = Query(None, description="Origin city"),
    destination: Optional[str] = Query(None, description="Destination city"),
    sort: Optional[str] = Query(None, description="Sort by: price_asc, price_desc, time_asc, time_desc"),
    db: AsyncSession = Depends(get_db)
):
    service = TripService(db)
    return await service.search_trips(origin, destination, sort)


# 🔵 مشاهده جزئیات سفر — عمومی
@router.get(
    "/{trip_id}",
    response_model=TripResponse,
    summary="🔍 مشاهده جزئیات سفر",
    description="همه کاربران می‌توانند اطلاعات سفر را مشاهده کنند."
)
async def get_trip(trip_id: int, db: AsyncSession = Depends(get_db)):
    service = TripService(db)
    trip = await service.get_trip(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


# ✏️ ویرایش سفر — فقط ادمین
@router.put(
    "/{trip_id}",
    response_model=TripResponse,
    summary="✏️ ویرایش سفر (فقط ادمین)",
    description="تنها ادمین می‌تواند اطلاعات سفر را ویرایش کند."
)
@require_role("admin")
async def update_trip(
    trip_id: int,
    data: TripUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = TripService(db)
    return await service.update_trip(trip_id, data)


# 🗑️ حذف سفر — فقط ادمین
@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_200_OK,
    summary="🗑️ حذف سفر (فقط ادمین)",
    description="تنها **ادمین** می‌تواند سفر را حذف کند."
)
@require_role("admin")
async def delete_trip(
    trip_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = TripService(db)
    return await service.delete_trip(trip_id)
