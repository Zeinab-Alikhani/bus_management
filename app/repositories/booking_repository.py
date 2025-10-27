from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, desc
from sqlalchemy.orm import joinedload
from app.models.booking import Booking
from app.models.trip import Trip


class BookingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # 🟢 ایجاد رزرو جدید
    async def create_booking(self, booking: Booking) -> Booking:
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    # 🟢 دریافت رزرو با ID
    async def get_booking_by_id(self, booking_id: int) -> Booking | None:
        result = await self.db.execute(select(Booking).where(Booking.id == booking_id))
        return result.scalars().first()

    # 🟢 لیست تمام رزروها
    async def list_bookings(self) -> list[Booking]:
        result = await self.db.execute(select(Booking))
        return result.scalars().all()

    # 🟢 بروزرسانی رزرو
    async def update_booking(self, booking: Booking) -> Booking:
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    # 🟢 حذف رزرو
    async def delete_booking(self, booking_id: int) -> bool:
        booking = await self.get_booking_by_id(booking_id)
        if booking:
            await self.db.delete(booking)
            await self.db.commit()
            return True
        return False

    # ✅ بررسی رزرو صندلی در یک سفر خاص
    async def get_booking_by_trip_and_seat(self, trip_id: int, seat_number: int):
        result = await self.db.execute(
            select(Booking)
            .where(Booking.trip_id == trip_id)
            .where(Booking.seat_number == seat_number)
        )
        return result.scalars().first()

    # ✅ فیلتر و مرتب‌سازی رزروها (بر اساس مبدا، مقصد و قیمت)
    async def get_filtered_bookings(self, origin=None, destination=None, sort=None):
        """
        origin: فیلتر بر اساس مبدأ (مثلاً 'Tehran')
        destination: فیلتر بر اساس مقصد (مثلاً 'Shiraz')
        sort: می‌تونه یکی از 'price_asc' یا 'price_desc' باشه
        """
        query = (
            select(Booking)
            .join(Trip, Trip.id == Booking.trip_id)
            .options(joinedload(Booking.trip))
        )

        # 🔹 اعمال فیلترها
        if origin:
            query = query.where(Trip.origin.ilike(f"%{origin}%"))
        if destination:
            query = query.where(Trip.destination.ilike(f"%{destination}%"))

        # 🔹 مرتب‌سازی بر اساس قیمت
        if sort == "price_asc":
            query = query.order_by(asc(Trip.price))
        elif sort == "price_desc":
            query = query.order_by(desc(Trip.price))

        result = await self.db.execute(query)
        return result.scalars().all()
