from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.db import get_session
from app.api.dependencies import get_current_user, get_current_github_token
from app.services.github.activity_service import sync_github_language_activity

router = APIRouter(
    prefix="/debug/github-activity",
    tags=["debug"],
)

@router.post("/sync")
async def sync_github_activity(
    language: str,
    days: int = 30,
    user = Depends(get_current_user),
    github_token: str = Depends(get_current_github_token),
):
    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(days=days)

    count = await sync_github_language_activity(
        user_id=user.id,
        github_token=github_token,
        language=language,
        from_date=from_date,
        to_date=to_date,
    )

    return {
        "days_synced": count,
        "language": language,
    }



