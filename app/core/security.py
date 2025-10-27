from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.db import AsyncSessionLocal
from app.utils.auth_utils import get_current_user


# ----------------------------------------
# تنظیمات JWT
# ----------------------------------------
SECRET_KEY = "supersecretkey"  # ⚠️ در حالت production از .env بگیر
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 روز

# ----------------------------------------
# OAuth2PasswordBearer
# ----------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ----------------------------------------
# اتصال به دیتابیس
# ----------------------------------------
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# ----------------------------------------
# bcrypt setup
# ----------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _safe_password(password) -> str:
    """bcrypt فقط تا ۷۲ بایت را قبول می‌کند."""
    if not isinstance(password, str):
        password = str(password)
    encoded = password.encode("utf-8", errors="ignore")
    if len(encoded) > 72:
        encoded = encoded[:72]
    return encoded.decode("utf-8", errors="ignore")


def get_password_hash(password) -> str:
    encoded = _safe_password(password)
    return pwd_context.hash(encoded)


def verify_password(plain_password, hashed_password) -> bool:
    plain_password = _safe_password(plain_password)
    return pwd_context.verify(plain_password, hashed_password)


# ----------------------------------------
# JWT creation and decoding
# ----------------------------------------
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ----------------------------------------
# استخراج کاربر از توکن JWT
# ----------------------------------------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    payload = decode_access_token(token)
    phone_number = payload.get("sub")

    if phone_number is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    result = await db.execute(select(User).where(User.phone_number == phone_number))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# ----------------------------------------
# کنترل نقش‌ها (Role-Based Access)
# ----------------------------------------
def require_role(*allowed_roles: str):
    """
    محدود کردن دسترسی بر اساس نقش کاربر.
    مثال استفاده:
        current_user = Depends(require_role("admin"))
        یا
        dependencies=[Depends(require_role("admin"))]
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        try:
            role = getattr(current_user.profile, "role", None)
            if role:
                role = getattr(role, "value", role)
        except Exception:
            role = None

        if not role or role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Allowed roles: {allowed_roles}"
            )
        return current_user

    return role_checker
