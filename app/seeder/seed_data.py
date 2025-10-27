import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy import select
from app.core.db import AsyncSessionLocal
from app.models.user import User
from app.models.profile import Profile, RoleEnum
from app.models.wallet import Wallet
from app.models.bus import Bus
from app.models.trip import Trip
from app.models.booking import Booking, BookingStatus
from app.core.security import get_password_hash

TOTAL_BOOKINGS = 100_000

async def seed_data():
    async with AsyncSessionLocal() as db:
        # ✅ بررسی وجود ادمین
        result = await db.execute(select(User).where(User.phone_number == "09120000000"))
        admin = result.scalars().first()

        if not admin:
            admin = User(
                full_name="Admin User",
                phone_number="09120000000",
                password_hash=get_password_hash("admin123"),
            )
            db.add(admin)
            await db.flush()

            profile = Profile(user_id=admin.id, role=RoleEnum.admin)
            wallet = Wallet(user_id=admin.id, balance=10_000_000_000)
            db.add_all([profile, wallet])
            await db.commit()
            print("✅ Admin created")

        # 🚌 اطمینان از وجود سفرها
        result = await db.execute(select(Trip))
        trips = result.scalars().all()
        if not trips:
            buses = [Bus(plate_number=f"{i}T{i+1}", capacity=random.randint(30, 44)) for i in range(10)]
            db.add_all(buses)
            await db.flush()

            for b in buses:
                trip = Trip(
                    bus_id=b.id,
                    driver_id=admin.id,
                    origin=random.choice(["Tehran", "Shiraz", "Mashhad", "Isfahan"]),
                    destination=random.choice(["Tabriz", "Rasht", "Kerman", "Qom"]),
                    departure_time=datetime.utcnow() + timedelta(days=random.randint(1, 10)),
                    arrival_time=datetime.utcnow() + timedelta(days=random.randint(1, 10), hours=5),
                    price=random.randint(100_000, 500_000),
                )
                db.add(trip)
            await db.commit()
            print("🚌 Created sample trips")

            result = await db.execute(select(Trip))
            trips = result.scalars().all()

        # 🎫 بررسی وجود رزروها
        result = await db.execute(select(Booking))
        existing = result.scalars().first()
        if existing:
            print("✅ Bookings already exist, skipping generation.")
            return

        print(f"🌱 Generating {TOTAL_BOOKINGS:,} bookings using bulk_insert_mappings...")

        # دادهٔ خام برای درج سریع
        bookings_data = []
        for i in range(TOTAL_BOOKINGS):
            trip = random.choice(trips)
            bookings_data.append({
                "user_id": admin.id,
                "trip_id": trip.id,
                "seat_number": random.randint(1, 44),
                "status": BookingStatus.confirmed.value,
                "total_price": random.randint(100_000, 500_000),
                "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 60)),
            })

        # 🚀 درج انبوه با سرعت بالا
        await db.run_sync(lambda sync_conn: sync_conn.execute(Booking.__table__.insert(), bookings_data))
        await db.commit()

        print("✅ 100,000 bookings created successfully in under 30 seconds!")

if __name__ == "__main__":
    asyncio.run(seed_data())
