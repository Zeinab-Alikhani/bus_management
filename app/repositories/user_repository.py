from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User).options(
                selectinload(User.profile),
                selectinload(User.wallet)
            ).where(User.id == user_id)
        )
        return result.scalars().first()

    async def get_user_by_phone(self, phone_number: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.phone_number == phone_number)
        )
        return result.scalars().first()

    async def get_all_users(self) -> list[User]:
        result = await self.db.execute(
            select(User).options(
                selectinload(User.profile),
                selectinload(User.wallet)
            )
        )
        return result.scalars().all()

    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(self, user_id: int, update_data):
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> bool:
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True
