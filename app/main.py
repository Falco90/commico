from typing import Annotated, Any
from datetime import datetime, timedelta, timezone
import httpx
from sqlmodel import Session, select

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, FastAPI, HTTPException, Security, Response
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ValidationError
from pwdlib import PasswordHash
from app.core.settings import settings
from app.core.db import engine
from app.core.security.encryption import encrypt_github_token, decrypt_github_token
from app.models.user import User
from app.models.github_account import GithubAccount
from app.services.github.client import fetch_github_activity
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
async def github_callback(code: str, response: Response):
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

        with Session(engine) as session:
            statement = select(GithubAccount).where(GithubAccount.github_id == github_user["id"])
            github_account = session.exec(statement).first()

            if github_account:
                user = session.get(User, github_account.user_id)

                if user is None:
                    raise HTTPException(
                        status_code=500,
                        detail="Database integrity error: GithubAccount without User"
                    )

                github_account.access_token_encrypted = encrypt_github_token(access_token)
            else:
                user = User()
                session.add(user)
                session.flush()

                github_account = GithubAccount(
                    user_id=user.id,
                    github_id=github_user["id"], 
                    github_username=github_user["login"], 
                    access_token_encrypted=encrypt_github_token(access_token))

                session.add(github_account)
            
            user_id = user.id
            encrypted_github_token = github_account.access_token_encrypted
            session.commit()
            
        decrypted_token = decrypt_github_token(encrypted_github_token)

        await fetch_github_activity(token=decrypted_token, from_date=datetime(2026, 1, 20, tzinfo=timezone.utc), to_date=datetime.now(tz=timezone.utc))

        jwt_token = create_access_token(data={"sub": str(user_id)}) 

        response.set_cookie(
            key="access_token",
            value=f"Bearer {jwt_token}",
            httponly=True,
            secure=False,        # False in local dev
            samesite="lax",
            max_age=60 * 60,    # 1 hour
        )

    return {"status": "successful", "detail": f"logged in as {user_id} with github id {github_user["id"]}"}

