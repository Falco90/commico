from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import date, timedelta

from app.agents.goal_insight_agent import generate_goal_insight
from app.core.db import get_session
from app.models.goal import Goal
from app.models.github_activity_day import GithubActivityDay
from app.schemas.goal import GoalCreate, GoalRead, GoalUpdate
from app.schemas.github_activity_day import GithubActivityDayRead
from app.services.goal.goal_service import (
    create_goal as create_goal_service,
    list_goals as list_goals_service,
    update_goal as update_goal_service,
)
from app.api.dependencies import get_current_user_id, get_current_user

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(
    data: GoalCreate,
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    return create_goal_service(session=session, user_id=user_id, data=data)


@router.get("", response_model=list[GoalRead])
def list_goals(
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    return list_goals_service(session=session, user_id=user_id)


@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(
    goal_id: int,
    data: GoalUpdate,
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    try:
        return update_goal_service(
            session=session,
            user_id=user_id,
            goal_id=goal_id,
            data=data,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Goal not found")


@router.get("/{goal_id}/insight")
async def get_goal_insight(
    goal_id: int,
    user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # 1️⃣ Load goal
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != user.id:
        raise HTTPException(status_code=404, detail="Goal not found")

    # 2️⃣ Define time window (last 14 days for now)
    to_date = date.today()
    from_date = to_date - timedelta(days=14)

    # 3️⃣ Load activity facts
    activity_days = session.exec(
        select(GithubActivityDay)
        .where(GithubActivityDay.user_id == user.id)
        .where(GithubActivityDay.language == goal.language)
        .where(GithubActivityDay.activity_date >= from_date)
        .where(GithubActivityDay.activity_date <= to_date)
        .order_by(GithubActivityDay.activity_date)
    ).all()

    activity_reads = [
        GithubActivityDayRead.model_validate(day)
        for day in activity_days
    ]

    # 4️⃣ Generate AI insight
    insight = await generate_goal_insight(
        goal=GoalRead.model_validate(goal),
        activity_days=activity_reads,
    )

    # 5️⃣ Return combined response
    return {
        "goal_id": goal.id,
        "language": goal.language,
        "from_date": from_date,
        "to_date": to_date,
        "activity_days": len(activity_reads),
        "insight": insight,
    }

