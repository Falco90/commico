from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import RedirectResponse

from app.services.github.github_oauth_service import github_oauth_login
from app.core.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/github/login")
async def github_login():
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_REDIRECT_URI:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub OAuth is not configured",
        )

    url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        "&scope=read:user user:email"
    )

    return RedirectResponse(url)


@router.get("/github/callback")
async def github_callback(code: str, response: Response):
    try:
        result = await github_oauth_login(code=code)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    response.set_cookie(
        key="access_token",
        value=f"Bearer {result.jwt}",
        httponly=True,
        secure=False,  # True in prod
        samesite="lax",
        max_age=60 * 60,
    )

    return {
        "status": "ok",
        "user_id": result.user_id,
        "new_user": result.is_new_user,
    }

