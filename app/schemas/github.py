from pydantic import BaseModel


class GithubLoginResult(BaseModel):
    user_id: int
    jwt: str
    is_new_user: bool


