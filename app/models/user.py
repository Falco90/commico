from sqlmodel import Field, SQLModel 
from typing import ClassVar

class User(SQLModel, table=True):
    __tablename__: ClassVar[str] = "users" # pyright: ignore[reportIncompatibleVariableOverride]
    id: int | None = Field(default=None, primary_key=True)
    github_id: int
    github_username: str
    email: str | None = Field(default=None)





