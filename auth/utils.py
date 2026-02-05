from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, expires_minutes: int = 60):
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"user_id": user_id, "exp": expire.timestamp()}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "expires": expire.isoformat()}
