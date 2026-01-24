from typing import Annotated, Any
from datetime import datetime, timedelta, timezone
import httpx
from sqlmodel import Session

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ValidationError
from pwdlib import PasswordHash
from app.core.settings import settings
from app.core.db import engine
from app.models.user import User

app = FastAPI()

def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()

    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update(
        {
            "exp": expire,
            "iat": now,
            "type": "access"
        }
    )

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    print(f"encoded jwt: {encoded_jwt}")
    return encoded_jwt


@app.get("/auth/github/login")
async def github_login():
    url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        "&scope=read:user user:email"
    )
    return RedirectResponse(url)

@app.get("/auth/github/callback")
async def github_callback(code: str):
    token_url = "https://github.com/login/oauth/access_token"
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            token_url,
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
            },
        )

    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Github token exchange failed")

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="No access token from Github")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Could not fetch Github user")

        github_user = user_response.json()

        user = User(github_id=github_user["id"], github_username=github_user["login"])
        print(f"User to db: {user}")
        
        session = Session(engine)
        session.add(user)
        session.commit()

        jwt_token = create_access_token(data={"sub": str(github_user["id"])})
        return {"status": "succesful", "detail": f"logged in as {github_user["login"]}"}


