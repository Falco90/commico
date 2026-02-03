from datetime import datetime, timezone, date
from typing import Iterable
from collections import defaultdict

from app.clients.github_graphql_client import (
    fetch_contributions_overview,
    fetch_repo_commit_dates,
)
from app.repositories.github_activity_repository import (
    upsert_github_activity_days,
)
from app.services.github.activity_logic import (
    extract_active_days,
    filter_repos_by_language,
    extract_commit_counts,
)


async def sync_github_language_activity(
    *,
    user_id: int,
    github_token: str,
    language: str,
    from_date: datetime,
    to_date: datetime,
    max_commits_per_repo: int = 100,
) -> int:
    overview = await fetch_contributions_overview(
        token=github_token,
        from_date=from_date,
        to_date=to_date,
    )

    active_days = extract_active_days(
        overview["contributionCalendar"]
    )

    if not active_days:
        return 0

    candidate_repos = filter_repos_by_language(
        overview["commitContributionsByRepository"],
        language=language,
    )

    if not candidate_repos:
        return 0

    daily_commit_counts: dict[date, int] = defaultdict(int)

    for repo in candidate_repos:
        owner = repo["repository"]["owner"]["login"]
        name = repo["repository"]["name"]

        commits = await fetch_repo_commit_dates(
            token=github_token,
            owner=owner,
            name=name,
            from_date=from_date,
            to_date=to_date,
            limit=max_commits_per_repo,
        )

        commit_counts = extract_commit_counts(commits)

        for day, count in commit_counts.items():
            daily_commit_counts[day] += count

    valid_days = active_days & daily_commit_counts.keys()

    final_counts = {
        day: daily_commit_counts[day]
        for day in valid_days
    }

    if not valid_days:
        return 0

    return upsert_github_activity_days(
        user_id=user_id,
        language=language,
        commit_counts=final_counts,
    )

