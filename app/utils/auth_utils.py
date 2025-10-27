from fastapi import Depends, HTTPException, status, Request
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.db import AsyncSessionLocal
from functools import wraps
from app.models.profile import RoleEnum


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    """
    گرفتن کاربر فعلی بر اساس توکن JWT از Header
    """
    # 🩵 import تنبل برای جلوگیری از circular import
    from app.core.security import oauth2_scheme, decode_access_token

    # ✅ گرفتن توکن واقعی از Header
    token = await oauth2_scheme(request)
    if not token:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    try:
        payload = decode_access_token(token)
        phone = payload.get("sub")
        role = payload.get("role")
        if not phone:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # ✅ جستجوی کاربر
    result = await db.execute(select(User).where(User.phone_number == phone))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not getattr(user, "profile", None):
        user.profile = type("TempProfile", (), {"role": RoleEnum(role or "passenger")})()

    return user


def require_role(*roles):
    """
    دکوراتور برای محدود کردن دسترسی endpointها بر اساس نقش کاربر.
    استفاده:
        @require_role("admin", "operator")
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = None

            # 🔹 جستجوی کاربر فعلی از آرگومان‌ها
            for arg in args:
                if hasattr(arg, "profile"):
                    current_user = arg
                    break

            if not current_user:
                current_user = kwargs.get("current_user")

            if not current_user:
                raise HTTPException(status_code=401, detail="User not authenticated")

            # 🔹 گرفتن نقش از profile
            user_role = None
            if hasattr(current_user, "profile") and current_user.profile:
                user_role = current_user.profile.role.value

            # 🔹 بررسی نقش مجاز
            if user_role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied for role '{user_role}' (required roles: {roles})"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
