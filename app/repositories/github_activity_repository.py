from datetime import date
from typing import Iterable

from sqlmodel import Session
from sqlalchemy.dialects.postgresql import insert

from app.core.db import engine
from app.models.github_activity_day import GithubActivityDay


def upsert_github_activity_days(
    *,
    user_id: int,
    language: str,
    days: Iterable[date],
    commit_count: int | None = None,
) -> int:
    rows = [
        {
            "user_id": user_id,
            "date": day,
            "language": language,
            "commit_count": commit_count,
        }
        for day in days
    ]

    if not rows:
        return 0

    stmt = (
        insert(GithubActivityDay)
        .values(rows)
        .on_conflict_do_update(
            index_elements=["user_id", "date", "language"],
            set_={
                "commit_count": commit_count,
            },
        )
    )

    with Session(engine) as session:
        result = session.exec(stmt)
        session.commit()

    return result.rowcount or 0

