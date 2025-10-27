from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.trip_repository import TripRepository
from app.models.bus import Bus
from app.models.profile import Profile

class TripService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TripRepository(db)

    async def create_trip(self, data):
        # بررسی وجود اتوبوس
        bus = await self.db.get(Bus, data.bus_id)
        if not bus:
            raise HTTPException(status_code=400, detail="Invalid bus_id — bus not found")

        # بررسی وجود راننده در صورت وجود driver_id
        if data.driver_id:
            driver = await self.db.get(Profile, data.driver_id)
            if not driver:
                raise HTTPException(status_code=400, detail="Invalid driver_id — driver not found")

        return await self.repo.create_trip(data)

    async def get_trip(self, trip_id: int):
        trip = await self.repo.get_trip_by_id(trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        return trip

    async def list_trips(self):
        return await self.repo.get_all_trips()

    async def update_trip(self, trip_id: int, data):
        trip = await self.repo.get_trip_by_id(trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        # اگر bus_id تغییر کرد، وجودش چک بشه
        if data.bus_id:
            bus = await self.db.get(Bus, data.bus_id)
            if not bus:
                raise HTTPException(status_code=400, detail="Invalid bus_id")

        if data.driver_id:
            driver = await self.db.get(Profile, data.driver_id)
            if not driver:
                raise HTTPException(status_code=400, detail="Invalid driver_id")

        return await self.repo.update_trip(trip_id, data)

    async def delete_trip(self, trip_id: int):
        deleted = await self.repo.delete_trip(trip_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Trip not found")
        return {"message": "Trip deleted successfully"}
    
    async def search_trips(self, origin=None, destination=None, sort=None):
        # ✅ متد اصلی جستجو
        return await self.repo.search_trips(origin, destination, sort)
