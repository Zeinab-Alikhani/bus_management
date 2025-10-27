from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import AppTransaction, TransactionType
from app.models.trip import Trip
from app.models.booking import Booking, BookingStatus
from app.models.transaction import AppTransaction, TransactionType
from app.models.profile import Profile
from sqlalchemy import desc


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ✅ مجموع درآمد کل از تراکنش‌های payment
    async def get_total_revenue(self):
        result = await self.db.execute(
            select(func.sum(AppTransaction.amount))
            .where(AppTransaction.transaction_type == TransactionType.payment)
        )
        total = result.scalar() or 0
        # چون پرداخت‌ها مقدار منفی هستند، باید قدر مطلق گرفته بشه
        return {"total_revenue": abs(float(total))}


 # ✅ درآمد بر اساس مسیر (origin → destination)
    async def get_revenue_by_route(self):
        from sqlalchemy import func, select
        from app.models.trip import Trip
        from app.models.booking import Booking
        from app.models.transaction import AppTransaction, TransactionType

        query = (
            select(
                Trip.origin,
                Trip.destination,
                func.sum(AppTransaction.amount).label("total_revenue")
            )
            .join(Booking, Booking.trip_id == Trip.id)
            .join(
                AppTransaction,
                AppTransaction.description.ilike(func.concat('%', Trip.id, '%'))
            )
            .where(AppTransaction.transaction_type == TransactionType.payment)
            .group_by(Trip.origin, Trip.destination)
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            {
                "origin": r.origin,
                "destination": r.destination,
                "total_revenue": abs(float(r.total_revenue))
            }
            for r in rows
        ]


# ✅ تعداد رزروهای ماه جاری
    async def get_monthly_bookings(self):
        query = (
            select(func.count(Booking.id))
            .where(Booking.status == BookingStatus.confirmed)
            .where(
                func.date_part('month', Booking.created_at)
                == func.date_part('month', func.now())
            )
            .where(
                func.date_part('year', Booking.created_at)
                == func.date_part('year', func.now())
            )
        )
        result = await self.db.execute(query)
        count = result.scalar() or 0
        return {"bookings_this_month": count}

 # ✅ راننده با بیشترین تعداد سفر
    async def get_top_driver(self):
        query = (
            select(
                Trip.driver_id,
                func.count(Trip.id).label("trip_count")
            )
            .where(Trip.driver_id.isnot(None))
            .group_by(Trip.driver_id)
            .order_by(desc(func.count(Trip.id)))
            .limit(1)
        )

        result = await self.db.execute(query)
        row = result.first()

        if not row:
            return {"message": "No driver data found"}

        # گرفتن پروفایل راننده و اطلاعات کاربرش
        driver_profile = await self.db.get(Profile, row.driver_id)
        driver_user = driver_profile.user if driver_profile else None

        # نام راننده از مدل User گرفته می‌شود
        driver_name = None
        if driver_user:
            driver_name = (
            getattr(driver_user, "username", None)
             or getattr(driver_user, "phone", None)
            or f"User #{driver_user.id}"
        )
        return {
            "driver_id": row.driver_id,
            "driver_name": driver_name,
            "role": driver_profile.role.value if driver_profile else None,
            "trip_count": int(row.trip_count)
        }