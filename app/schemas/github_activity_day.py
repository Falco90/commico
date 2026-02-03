from datetime import date, datetime
from sqlmodel import SQLModel

class GithubActivityDayBase(SQLModel):
    activity_date: date
    language: str
    commit_count: int


class GithubActivityDayRead(GithubActivityDayBase):
    id: int
    user_id: int
    created_at: datetime

