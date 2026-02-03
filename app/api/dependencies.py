from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.security.jwt import decode_access_token
from app.models.user import User

# app/api/dependencies.py

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.security.jwt import decode_access_token
from app.models.user import User


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> User:
    raw = request.cookies.get("access_token")
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = raw.removeprefix("Bearer ").strip()
    user_id = decode_access_token(token)

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user



def get_current_user_id(
    user: User = Depends(get_current_user),
) -> int:
    return user.id

