from app.repositories.bus_repository import BusRepository
from app.models.profile import Profile
from fastapi import HTTPException

class BusService:
    def __init__(self, db):
        self.db = db
        self.repo = BusRepository(db)

    async def create_bus(self, data):
        # بررسی تکراری نبودن پلاک
        buses = await self.repo.get_all_buses()
        if any(bus.plate_number == data.plate_number for bus in buses):
            raise HTTPException(status_code=400, detail="Bus with this plate number already exists")

        # بررسی معتبر بودن راننده
        if data.operator_id:
            operator = await self.db.get(Profile, data.operator_id)
            if not operator:
                raise HTTPException(status_code=400, detail="Invalid operator_id")
        
        return await self.repo.create_bus(data)

    async def get_all_buses(self):
        return await self.repo.get_all_buses()

    async def get_bus_by_id(self, bus_id: int):
        bus = await self.repo.get_bus_by_id(bus_id)
        if not bus:
            raise HTTPException(status_code=404, detail="Bus not found")
        return bus

    async def update_bus(self, bus_id: int, data):
        bus = await self.repo.get_bus_by_id(bus_id)
        if not bus:
            raise HTTPException(status_code=404, detail="Bus not found")

        if data.operator_id:
            operator = await self.db.get(Profile, data.operator_id)
            if not operator:
                raise HTTPException(status_code=400, detail="Invalid operator_id")

        updated_bus = await self.repo.update_bus(bus_id, data)
        return updated_bus

    async def delete_bus(self, bus_id: int):
        bus = await self.repo.get_bus_by_id(bus_id)
        if not bus:
            raise HTTPException(status_code=404, detail="Bus not found")

        await self.repo.delete_bus(bus_id)
        return {"message": f"Bus with id={bus_id} deleted successfully"}
