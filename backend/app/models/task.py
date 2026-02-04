"""Task model for todo application."""
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """Task model with user ownership and completion tracking."""

    __tablename__ = "tasks"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False
    )
    user_id: UUID = Field(
        foreign_key="users.user_id",
        nullable=False,
        index=True
    )
    title: str = Field(
        min_length=1,
        max_length=255,
        nullable=False
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000
    )
    completed: bool = Field(
        default=False,
        nullable=False
    )
    priority: str = Field(
        default="medium",
        nullable=False,
        max_length=10
    )
    due_date: Optional[datetime] = Field(
        default=None
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
