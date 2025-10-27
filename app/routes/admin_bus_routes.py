from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import AsyncSessionLocal
from app.schemas.bus import BusCreate, BusResponse
from app.services.bus_service import BusService
from app.core.security import require_role
from app.models.user import User

router = APIRouter(prefix="/api/admin/buses", tags=["Admin - Buses"])

# 🔹 Dependency برای سشن دیتابیس
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# 🚌 فقط ادمین اجازه ایجاد اتوبوس دارد
@router.post("/create", response_model=BusResponse)
async def create_bus(
    data: BusCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    service = BusService(db)
    bus = await service.create_bus(data)
    return bus
