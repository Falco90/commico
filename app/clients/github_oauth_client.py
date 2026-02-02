import httpx

from app.core.settings import settings

GITHUB_OAUTH_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_BASE_URL = "https://api.github.com"


class GithubOAuthError(RuntimeError):
    pass


async def exchange_code_for_token(*, code: str) -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            GITHUB_OAUTH_TOKEN_URL,
            headers={
                "Accept": "application/json",
            },
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
            },
        )

    if response.status_code != 200:
        raise GithubOAuthError(
            f"GitHub token exchange failed: {response.status_code} {response.text}"
        )

    payload = response.json()
    token = payload.get("access_token")

    if not token:
        raise GithubOAuthError(
            f"No access token returned by GitHub: {payload}"
        )

    return token


async def fetch_github_user(*, token: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{GITHUB_API_BASE_URL}/user",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )

    if response.status_code != 200:
        raise GithubOAuthError(
            f"Failed to fetch GitHub user: {response.status_code} {response.text}"
        )

    return response.json()

