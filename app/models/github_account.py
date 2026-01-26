from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, func, BigInteger, ForeignKey
from typing import ClassVar
from datetime import datetime

class GithubAccount(SQLModel, table=True):
    __tablename__: ClassVar[str] = "github_accounts" # pyright: ignore[reportIncompatibleVariableOverride]
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            index=True
        )
    )
    github_id: int = Field(index=True, unique=True)
    github_username: str
    access_token_encrypted: str
    token_scopes: str | None = None
    revoked_at: datetime | None = None
    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )
    updated_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
    )

 

