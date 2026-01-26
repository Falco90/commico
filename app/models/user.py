from sqlmodel import Field, SQLModel
from datetime import datetime
from sqlalchemy import Column, DateTime, func
from typing import ClassVar

class User(SQLModel, table=True):
    __tablename__: ClassVar[str] = "users" # pyright: ignore[reportIncompatibleVariableOverride]
    id: int | None = Field(default=None, primary_key=True)
    email: str | None = Field(default=None)
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





