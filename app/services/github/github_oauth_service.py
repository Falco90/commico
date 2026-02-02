from sqlmodel import Session

from app.core.db import engine
from app.core.security.encryption import encrypt_github_token, create_access_token
from app.clients.github_oauth_client import (
    exchange_code_for_token,
    fetch_github_user,
)
from app.repositories.github_account_repository import (
    get_github_account_by_github_id,
    create_user_with_github_account,
    update_github_access_token,
)

from app.schemas.github import GithubLoginResult


async def github_oauth_login(*, code: str) -> GithubLoginResult:
    github_token = await exchange_code_for_token(code=code)
    github_user = await fetch_github_user(token=github_token)

    encrypted_token = encrypt_github_token(github_token)

    with Session(engine) as session:
        github_account = get_github_account_by_github_id(
            session,
            github_id=github_user["id"],
        )

        if github_account:
            update_github_access_token(
                session,
                github_account=github_account,
                encrypted_access_token=encrypted_token,
            )
            user_id = github_account.user_id
            is_new_user = False
        else:
            user = create_user_with_github_account(
                session,
                github_id=github_user["id"],
                github_username=github_user["login"],
                encrypted_access_token=encrypted_token,
            )
            user_id = user.id
            is_new_user = True

    jwt = create_access_token({"sub": str(user_id)})

    return GithubLoginResult(
        user_id=user_id,
        jwt=jwt,
        is_new_user=is_new_user,
    )

