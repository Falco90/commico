from datetime import date, timedelta
from typing import Iterable

from app.schemas.goal import GoalRead
from app.schemas.github_activity_day import GithubActivityDayRead
from app.agents.llm_clients.huggingface_client import HuggingFaceClient


_llm = HuggingFaceClient(model="google/flan-t5-large")


async def generate_goal_insight(
    *,
    goal: GoalRead,
    activity_days: Iterable[GithubActivityDayRead],
) -> str:
    """
    Generate a motivational insight for a user's goal,
    based on recent GitHub activity.
    """

    activity_days = list(activity_days)

    # --- derive facts from activity ---
    today = date.today()
    last_week_start = today - timedelta(days=7)

    recent_dates = [day.activity_date for day in activity_days]

    active_days_last_week = len(
        {d for d in recent_dates if d >= last_week_start}
    )

    recent_days_str = (
        ", ".join(d.isoformat() for d in sorted(recent_dates))
        if recent_dates
        else "No activity recorded."
    )

    # --- build prompt ---
    prompt = f"""
You are a supportive developer productivity coach.

The user has a goal:
- Language: {goal.language}
- Target: {goal.target_days_per_week} days per week

Last week:
- Active days: {active_days_last_week}

Recent activity days:
{recent_days_str}

Rules:
- Be concise (3–5 sentences)
- Be encouraging, not judgmental
- Give one concrete improvement suggestion
- Do NOT mention tracking systems, GitHub, or databases

Insight:
""".strip()

    return await _llm.generate(prompt)

