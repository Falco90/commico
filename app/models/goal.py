from sqlalchemy import Column, DateTime, func
from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import ClassVar
from app.core.models.user import User
from datetime import date

class Goal(SQLModel, table=True):
    __tablename__: ClassVar[str] = "goals" # pyright: ignore[reportIncompatibleVariableOverride]
    id: str | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key=User.id)
    language: str
    target_days_per_week: int
    start_date: datetime 
    active: bool
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
            nullable=False,
        )
    )





