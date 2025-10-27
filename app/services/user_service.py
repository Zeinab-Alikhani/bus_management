from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.models.profile import Profile, RoleEnum
from app.models.wallet import Wallet
from app.schemas.user import UserCreate
from fastapi import HTTPException

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def register_user(self, user_data: UserCreate):
        # بررسی شماره تکراری
        existing = await self.repo.get_user_by_phone(user_data.phone_number)
        if existing:
            raise HTTPException(status_code=400, detail="Phone number already registered")

        # ساخت آبجکت‌ها
        user = User(
            full_name=user_data.full_name,
            phone_number=user_data.phone_number
        )
        profile = Profile(user=user, role=RoleEnum.passenger)
        wallet = Wallet(user=user, balance=0.00)

        # افزودن و commit نهایی
        self.db.add_all([user, profile, wallet])
        await self.db.commit()
        await self.db.refresh(user)

        # برگردوندن یوزر با روابطش
        return await self.repo.get_user_by_id(user.id)

    async def get_user(self, user_id: int):
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def list_users(self):
        return await self.repo.get_all_users()
    
    async def update_user(self, user_id: int, data):
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # اگر شماره تلفن تکراریه:
        if data.phone_number:
            existing = await self.repo.get_user_by_phone(data.phone_number)
            if existing and existing.id != user_id:
                raise HTTPException(status_code=400, detail="Phone number already exists")

        return await self.repo.update_user(user_id, data)

    async def delete_user(self, user_id: int):
        deleted = await self.repo.delete_user(user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
