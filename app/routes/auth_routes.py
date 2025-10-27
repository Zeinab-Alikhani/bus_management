from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import AsyncSessionLocal
from app.models.user import User
from app.models.profile import Profile, RoleEnum
from app.schemas.auth import TokenResponse, LoginRequest, RegisterRequest
from app.core.security import create_access_token, get_password_hash, verify_password
from fastapi import Body
from app.models.wallet import Wallet
from app.utils.auth_utils import get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# 🟢 ثبت‌نام کاربر جدید
@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone_number == data.phone_number))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    # ✅ ساخت کاربر با رمز هش‌شده
    user = User(
        full_name=data.full_name,
        phone_number=data.phone_number,
        password_hash=get_password_hash(str(data.password))
    )
    db.add(user)
    await db.flush()

    # ✅ نقش پیش‌فرض passenger
    profile = Profile(user_id=user.id, role=RoleEnum.passenger)
    db.add(profile)
    # ✅ ایجاد خودکار کیف پول
    wallet = Wallet(user_id=user.id, balance=0)
    db.add(wallet)
    await db.commit()
    await db.refresh(user)

    # 🔐 تولید توکن JWT شامل role و id
    token_data = {
        "sub": user.phone_number,
        "user_id": user.id,
        "role": profile.role.value
    }
    token = create_access_token(token_data)

    return {"access_token": token, "token_type": "bearer"}


# 🟢 ورود کاربر (Login)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: dict = Body(..., example={"phone_number": "09120000000", "password": "1234"}),
    db: AsyncSession = Depends(get_db)
):
    phone_number = credentials.get("phone_number")
    password = credentials.get("password")

    if not phone_number or not password:
        raise HTTPException(status_code=400, detail="Phone number and password are required")

    result = await db.execute(select(User).where(User.phone_number == phone_number))
    user = result.scalars().first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {
    "sub": user.phone_number,
    "user_id": user.id,
    "role": user.profile.role.value if user.profile else "passenger"
    }
    token = create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer"}



# 🟢 اطلاعات کاربر لاگین‌شده
@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    profile_role = (
        current_user.profile.role.value
        if current_user.profile else "unknown"
    )

    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "phone_number": current_user.phone_number,
        "role": profile_role,
        "created_at": current_user.created_at,
    }
