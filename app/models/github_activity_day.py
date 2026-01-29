from sqlmodel import SQLModel, Field
from datetime import date, datetime
from sqlalchemy import UniqueConstraint, Column, DateTime, func
from typing import ClassVar

class GithubActivityDay(SQLModel, table=True):
    __tablename__: ClassVar[str] = "github_activity_days" # pyright: ignore[reportIncompatibleVariableOverride]
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "date",
            "language",
            name="uq_github_activity_day_user_date_language",
        ),
    )
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    date: date = Field(index=True)
    language: str = Field(index=True)
    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )

