from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.bus import Bus

class BusRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_bus(self, bus_data):
        new_bus = Bus(**bus_data.dict())
        self.db.add(new_bus)
        await self.db.commit()
        await self.db.refresh(new_bus)
        return new_bus

    async def get_all_buses(self):
        result = await self.db.execute(select(Bus))
        return result.scalars().all()

    async def get_bus_by_id(self, bus_id: int):
        result = await self.db.execute(select(Bus).where(Bus.id == bus_id))
        return result.scalar_one_or_none()

    async def update_bus(self, bus_id: int, update_data):
        bus = await self.get_bus_by_id(bus_id)
        if not bus:
            return None

        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(bus, key, value)

        await self.db.commit()
        await self.db.refresh(bus)
        return bus

    async def delete_bus(self, bus_id: int):
        bus = await self.get_bus_by_id(bus_id)
        if bus:
            await self.db.delete(bus)
            await self.db.commit()
            return True
        return False
