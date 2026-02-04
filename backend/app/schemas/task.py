"""Task schemas for request/response validation."""
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(
        min_length=1,
        max_length=255,
        description="Task title (required, 1-255 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (optional, max 1000 characters)"
    )
    priority: Optional[str] = Field(
        default="medium",
        description="Task priority (optional, default: medium)",
        pattern=r"^(low|medium|high)$"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Task due date (optional)"
    )


class TaskUpdate(BaseModel):
    """Schema for updating an existing task (partial updates supported)."""

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Task title (optional)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Task description (optional)"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Task completion status (optional)"
    )
    priority: Optional[str] = Field(
        default=None,
        description="Task priority (optional)",
        pattern=r"^(low|medium|high)$"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Task due date (optional)"
    )


class TaskPublic(BaseModel):
    """Schema for task responses."""

    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
