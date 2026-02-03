from __future__ import annotations

from datetime import datetime, date
from typing import Iterable
from collections import defaultdict

from app.clients.github_graphql_client import (
    fetch_contributions_overview,
    fetch_repo_commit_dates,
)


def extract_active_days(contribution_calendar: dict) -> set[date]:
    active_days: set[date] = set()

    for week in contribution_calendar["weeks"]:
        for day in week["contributionDays"]:
            if day["contributionCount"] > 0:
                active_days.add(date.fromisoformat(day["date"]))

    return active_days


def filter_repos_by_language(
    commit_contributions: Iterable[dict],
    *,
    language: str,
) -> list[dict]:
    return [
        repo
        for repo in commit_contributions
        if repo["repository"].get("primaryLanguage")
        and repo["repository"]["primaryLanguage"]["name"] == language
    ]

from collections import defaultdict
from datetime import date, datetime
from typing import Iterable


def extract_commit_counts(
    commits: Iterable[datetime],
) -> dict[date, int]:
    counts: dict[date, int] = defaultdict(int)

    for committed_at in commits:
        day = committed_at.date()
        counts[day] += 1

    return counts

async def collect_language_activity_days(
    *,
    token: str,
    goal_language: str,
    from_date: datetime,
    to_date: datetime,
    max_commits_per_repo: int = 100,
) -> set[date]:
    overview = await fetch_contributions_overview(
        token=token,
        from_date=from_date,
        to_date=to_date,
    )

    active_days = extract_active_days(
        overview["contributionCalendar"]
    )

    if not active_days:
        return set()

    candidate_repos = filter_repos_by_language(
        overview["commitContributionsByRepository"],
        language=goal_language,
    )

    if not candidate_repos:
        return set()

    commit_days: set[date] = set()

    for repo in candidate_repos:
        owner = repo["repository"]["owner"]["login"]
        name = repo["repository"]["name"]

        commits = await fetch_repo_commit_dates(
            token=token,
            owner=owner,
            name=name,
            from_date=from_date,
            to_date=to_date,
            limit=max_commits_per_repo,
        )

        commit_days |= extract_commit_days(commits)

    return active_days & commit_days

