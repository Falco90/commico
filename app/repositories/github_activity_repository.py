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
    commit_counts: dict[date, int],
) -> int:
    rows = [
        {
            "user_id": user_id,
            "activity_date": day,
            "language": language,
            "commit_count": count,
        }
        for day, count in commit_counts.items() 
    ]

    if not rows:
        return 0
    
    insert_stmt = insert(GithubActivityDay)

    stmt = insert_stmt.values(rows).on_conflict_do_update(
        index_elements=["user_id", "activity_date", "language"],
        set_={
            "commit_count": insert_stmt.excluded.commit_count,
        },
    )

    with Session(engine) as session:
        result = session.exec(stmt)
        session.commit()

    return result.rowcount or 0

