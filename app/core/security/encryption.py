from cryptography.fernet import Fernet
from app.core.settings import settings
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt

fernet = Fernet(settings.GITHUB_TOKEN_ENCRYPTION_KEY)

def encrypt_github_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_github_token(token_encrypted: str) -> str:
    return fernet.decrypt(token_encrypted.encode()).decode()

def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()

    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update(
        {
            "exp": expire,
            "iat": now,
            "type": "access"
        }
    )

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt

