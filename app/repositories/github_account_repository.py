from typing import Optional

from sqlmodel import Session, select

from app.models.user import User
from app.models.github_account import GithubAccount

def get_github_account_by_github_id(
    session: Session,
    *,
    github_id: int,
) -> GithubAccount | None:
    statement = select(GithubAccount).where(
        GithubAccount.github_id == github_id
    )
    return session.exec(statement).first()

def get_github_account_for_user(
    *,
    session: Session,
    user_id: int,
) -> GithubAccount | None:
    statement = select(GithubAccount).where(
        GithubAccount.user_id == user_id,
        GithubAccount.revoked_at.is_(None),
    )
    return session.exec(statement).first()

def get_user_by_id(
    session: Session,
    *,
    user_id: int,
) -> User | None:
    return session.get(User, user_id)


def create_user_with_github_account(
    session: Session,
    *,
    github_id: int,
    github_username: str,
    encrypted_access_token: str,
) -> User:
    user = User()
    session.add(user)
    session.flush()  # assigns user.id

    github_account = GithubAccount(
        user_id=user.id,
        github_id=github_id,
        github_username=github_username,
        access_token_encrypted=encrypted_access_token,
    )

    session.add(github_account)
    session.commit()

    return user


def update_github_access_token(
    session: Session,
    *,
    github_account: GithubAccount,
    encrypted_access_token: str,
) -> None:
    github_account.access_token_encrypted = encrypted_access_token
    session.commit()


def revoke_github_account(
    session: Session,
    *,
    github_account: GithubAccount,
) -> None:
    from datetime import datetime, timezone

    github_account.revoked_at = datetime.now(timezone.utc)
    session.commit()

