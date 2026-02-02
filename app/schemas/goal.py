from datetime import date
from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    language: str = Field(..., example="Rust")
    target_days_per_week: int = Field(..., ge=1, le=7)
    start_date: date


class GoalUpdate(BaseModel):
    target_days_per_week: int | None = Field(None, ge=1, le=7)
    active: bool | None = None


class GoalRead(BaseModel):
    id: int
    language: str
    target_days_per_week: int
    start_date: date
    active: bool

    class Config:
        from_attributes = True

