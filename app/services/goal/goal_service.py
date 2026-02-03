from sqlmodel import Session
from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalUpdate
from app.repositories.goal_repository import (
    create_goal_for_user,
    list_goals_by_user,
    get_goal_for_user,
)


def create_goal(
    *,
    session: Session,
    user_id: int,
    data: GoalCreate,
) -> Goal:
    goal = Goal(
        user_id=user_id,
        language=data.language,
        target_days_per_week=data.target_days_per_week,
        start_date=data.start_date,
        active=True,
    )

    return create_goal_for_user(session=session, goal=goal)


def list_goals(
    *,
    session: Session,
    user_id: int,
) -> list[Goal]:
    return list_goals_by_user(session=session, user_id=user_id)


def update_goal(
    *,
    session: Session,
    user_id: int,
    goal_id: int,
    data: GoalUpdate,
) -> Goal:
    goal = get_goal_for_user(
        session=session,
        user_id=user_id,
        goal_id=goal_id,
    )

    if not goal:
        raise ValueError("Goal not found")

    if data.target_days_per_week is not None:
        goal.target_days_per_week = data.target_days_per_week

    if data.active is not None:
        goal.active = data.active

    session.commit()
    session.refresh(goal)
    return goal

