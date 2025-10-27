from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import AsyncSessionLocal
from app.schemas.trip import TripCreate, TripRead
from app.services.trip_service import TripService
from app.core.security import require_role

router = APIRouter(prefix="/admin/trips", tags=["Admin - Trips"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/create", dependencies=[Depends(require_role("admin"))])
async def create_trip(data: TripCreate, db: AsyncSession = Depends(get_db)):
    service = TripService(db)
    return await service.create_trip(data)



