from datetime import datetime, timedelta, timezone
from sqlmodel import Session

from app.core.db import engine
from app.repositories.goal_repository import list_active_goals
from app.repositories.github_account_repository import get_github_account_for_user
from app.services.github.activity_service import sync_github_language_activity
from app.core.security.encryption import decrypt_github_token

async def run_github_activity_sync(days: int):
    now = datetime.now(timezone.utc)
    from_date = now - timedelta(days=days)  
    to_date = now

    with Session(engine) as session:
        goals = list_active_goals(session)

        for goal in goals:
            github_account = get_github_account_for_user(
                session=session,
                user_id=goal.user_id,
            )

            if not github_account or github_account.revoked_at:
                continue

            github_token = decrypt_github_token(
                github_account.access_token_encrypted
            )

            await sync_github_language_activity(
                user_id=goal.user_id,
                github_token=github_token,
                language=goal.language,
                from_date=from_date,
                to_date=to_date,
            )

