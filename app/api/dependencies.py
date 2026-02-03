from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.security.jwt import decode_access_token
from app.core.security.encryption import decrypt_github_token
from app.models.user import User
from app.models.github_account import GithubAccount

# app/api/dependencies.py

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session, select

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


async def get_current_github_token(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> str:
    github_account = session.exec(
        select(GithubAccount).where(GithubAccount.user_id == user.id)
    ).first()

    if not github_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no connected GitHub account",
        )

    return decrypt_github_token(github_account.access_token_encrypted)
