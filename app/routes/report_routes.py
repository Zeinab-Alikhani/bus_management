from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/total-revenue")
async def total_revenue(db: AsyncSession = Depends(get_db)):  # ✅ باید دقیقاً این باشه
    service = ReportService(db)
    return await service.get_total_revenue()

@router.get("/revenue-by-route")
async def revenue_by_route(db: AsyncSession = Depends(get_db)):
    service = ReportService(db)
    return await service.get_revenue_by_route()

@router.get("/monthly-bookings")
async def monthly_bookings(db: AsyncSession = Depends(get_db)):
    service = ReportService(db)
    return await service.get_monthly_bookings()

@router.get("/top-driver")
async def top_driver(db: AsyncSession = Depends(get_db)):
    service = ReportService(db)
    return await service.get_top_driver()

