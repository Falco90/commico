from sqlmodel import Field, SQLModel 

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    github_id: int
    github_username: str
    email: str





