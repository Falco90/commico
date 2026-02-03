from __future__ import annotations

from datetime import date
from typing import Iterable
from app.core.settings import settings

from openai import AsyncOpenAI

from app.schemas.goal import GoalRead
from app.schemas.github_activity_day import GithubActivityDayRead


client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def _summarize_activity(
    *,
    activity_days: Iterable[GithubActivityDayRead],
) -> dict:
    """
    Convert raw activity rows into compact stats for the LLM.
    """
    days = list(activity_days)

    if not days:
        return {
            "total_days": 0,
            "total_commits": 0,
            "avg_commits_per_day": 0,
            "activity_dates": [],
        }

    total_commits = sum(d.commit_count for d in days)

    return {
        "total_days": len(days),
        "total_commits": total_commits,
        "avg_commits_per_day": round(total_commits / len(days), 2),
        "activity_dates": [d.activity_date.isoformat() for d in days],
    }


def _build_prompt(
    *,
    goal: GoalRead,
    summary: dict,
) -> str:
    return f"""
You are a supportive but honest programming goal coach.

The user has the following goal:
- Language: {goal.language}
- Target active days per week: {goal.target_days_per_week}

Recent GitHub activity summary:
- Active days: {summary["total_days"]}
- Total commits: {summary["total_commits"]}
- Average commits per active day: {summary["avg_commits_per_day"]}
- Dates active: {", ".join(summary["activity_dates"]) or "none"}

Rules:
- Be concise (max 6 sentences)
- Be encouraging, not judgmental
- If the user is behind, suggest a realistic adjustment
- If they are on track, reinforce the habit
- Do NOT invent data
- Do NOT mention GitHub explicitly

Explain how the user is doing and give 1 actionable suggestion.
""".strip()


async def generate_goal_insight(
    *,
    goal: GoalRead,
    activity_days: Iterable[GithubActivityDayRead],
) -> str:
    """
    Generate a natural-language insight about goal progress.
    """

    summary = _summarize_activity(activity_days=activity_days)

    prompt = _build_prompt(
        goal=goal,
        summary=summary,
    )

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful coaching assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=200,
    )

    return response.choices[0].message.content.strip()

