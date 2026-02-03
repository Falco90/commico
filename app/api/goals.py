from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.db import get_session
from app.schemas.goal import GoalCreate, GoalRead, GoalUpdate
from app.services.goal.goal_service import (
    create_goal as create_goal_service,
    list_goals as list_goals_service,
    update_goal as update_goal_service,
)
from app.api.dependencies import get_current_user_id

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

