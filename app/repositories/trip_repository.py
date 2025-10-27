from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.trip import Trip
from sqlalchemy import select, func, asc, desc
from sqlalchemy.orm import joinedload
from app.models.trip import Trip
from app.models.bus import Bus
from app.models.booking import Booking

class TripRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_trip(self, trip_data):
        new_trip = Trip(**trip_data.dict())
        self.db.add(new_trip)
        await self.db.commit()
        await self.db.refresh(new_trip)
        return new_trip

    async def get_trip_by_id(self, trip_id: int):
        result = await self.db.execute(select(Trip).where(Trip.id == trip_id))
        return result.scalars().first()

    async def get_all_trips(self):
        result = await self.db.execute(select(Trip))
        return result.scalars().all()
    
    async def update_trip(self, trip_id: int, update_data):
        trip = await self.get_trip_by_id(trip_id)
        if not trip:
            return None
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(trip, key, value)
        await self.db.commit()
        await self.db.refresh(trip)
        return trip
    
    async def delete_trip(self, trip_id: int):
        trip = await self.get_trip_by_id(trip_id)
        if trip:
            await self.db.delete(trip)
            await self.db.commit()
            return True
        return False




    async def search_trips(self, origin=None, destination=None, sort=None):
        query = (
            select(Trip)
            .options(joinedload(Trip.bus))
        )

        # فیلتر بر اساس مبدأ و مقصد
        if origin:
            query = query.where(Trip.origin.ilike(f"%{origin}%"))
        if destination:
            query = query.where(Trip.destination.ilike(f"%{destination}%"))

        # مرتب‌سازی
        if sort == "price_asc":
            query = query.order_by(asc(Trip.price))
        elif sort == "price_desc":
            query = query.order_by(desc(Trip.price))
        elif sort == "time_asc":
            query = query.order_by(asc(Trip.departure_time))
        elif sort == "time_desc":
            query = query.order_by(desc(Trip.departure_time))

        result = await self.db.execute(query)
        trips = result.scalars().all()

        # فیلتر ظرفیت (بر اساس رزروها)
        available_trips = []
        for trip in trips:
            booked_count = await self.db.scalar(
                select(func.count(Booking.id)).where(Booking.trip_id == trip.id)
            )
            if booked_count < trip.bus.capacity:
                available_trips.append(trip)

        return available_trips