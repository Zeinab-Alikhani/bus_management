from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import AsyncSessionLocal

# مدل موقت برای شبیه‌سازی کاربر فعلی
class FakeUser:
    def __init__(self, user_id: int, role: str = "admin"):
        self.id = user_id
        self.role = role


# وابستگی دیتابیس
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# تابع موقت برای بازگرداندن کاربر فعلی (فعلاً بدون JWT)
async def get_current_user(db: AsyncSession = Depends(get_db)):
    """
    فعلاً به صورت موقت همیشه کاربر ادمین برمی‌گردد.
    بعداً با JWT جایگزین می‌کنیم.
    """
    return FakeUser(user_id=1, role="admin")
