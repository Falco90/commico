from sqlmodel import Session, select
from app.models.goal import Goal


def create_goal_for_user(*, session: Session, goal: Goal) -> Goal:
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


def list_goals_by_user(*, session: Session, user_id: int) -> list[Goal]:
    statement = select(Goal).where(Goal.user_id == user_id)
    return list(session.exec(statement))


def get_goal_for_user(
    *,
    session: Session,
    user_id: int,
    goal_id: int,
) -> Goal | None:
    statement = (
        select(Goal)
        .where(Goal.id == goal_id)
        .where(Goal.user_id == user_id)
    )
    return session.exec(statement).first()

