from datetime import date, datetime, timedelta, timezone

import requests
from sqlmodel import Session, select

from app.core.security.encryption import decrypt_github_token
from app.models.user import User
from app.models.github_activity import GithubActivityDay


GITHUB_API_BASE = "https://api.github.com"


def sync_github_activity_for_user(
    *,
    session: Session,
    user_id: int,
    from_date: date | None = None,
    to_date: date | None = None,
) -> None:
    """
    Fetch GitHub activity for a user and persist it as daily aggregates.

    This function is intentionally:
    - synchronous
    - side-effectful
    - callable from API, worker, or CLI
    """

    user = session.get(User, user_id)
    if not user or not user.github_access_token_encrypted:
        return  # nothing to sync

    github_token = decrypt_github_token(user.github_access_token_encrypted)

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }

    # Default range: last 30 days
    if not to_date:
        to_date = date.today()

    if not from_date:
        from_date = to_date - timedelta(days=30)

    # GitHub expects ISO timestamps
    since = datetime.combine(from_date, datetime.min.time(), tzinfo=timezone.utc)
    until = datetime.combine(to_date, datetime.max.time(), tzinfo=timezone.utc)

    events = _fetch_user_events(headers=headers, since=since)

    daily_counts: dict[date, int] = {}

    for event in events:
        created_at = datetime.fromisoformat(
            event["created_at"].replace("Z", "+00:00")
        )

        if created_at < since or created_at > until:
            continue

        day = created_at.date()
        daily_counts[day] = daily_counts.get(day, 0) + 1

    _upsert_daily_activity(
        session=session,
        user_id=user_id,
        daily_counts=daily_counts,
    )

    session.commit()

