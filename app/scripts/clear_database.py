import asyncio
from sqlalchemy import text
from app.core.db import engine

# ⚠️ هشدار: این اسکریپت تمام داده‌ها را پاک می‌کند!
# فقط برای محیط تست یا توسعه استفاده شود.

async def clear_database():
    async with engine.begin() as conn:
        print("🚨 پاک‌سازی داده‌ها در حال انجام است...")
        await conn.execute(text("""
        TRUNCATE TABLE
            bookings,
            trips,
            buses,
            wallets,
            transactions,
            profiles,
            users
        RESTART IDENTITY CASCADE;
        """))
        print("✅ تمام داده‌ها پاک شدند و شمارنده ID ریست شد.")

if __name__ == "__main__":
    asyncio.run(clear_database())
