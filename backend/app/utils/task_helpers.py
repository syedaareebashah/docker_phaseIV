"""Task helper utilities for ownership verification."""
from uuid import UUID
from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..models.task import Task


def get_task_or_404(task_id: UUID, user_id: UUID, session: Session) -> Task:
    """
    Retrieve a task by ID with ownership verification.

    Returns 404 if task doesn't exist OR if it belongs to a different user.
    This prevents revealing the existence of other users' tasks.

    Args:
        task_id: Task ID to retrieve
        user_id: User ID that must own the task
        session: Database session

    Returns:
        Task object if found and owned by user

    Raises:
        HTTPException: 404 Not Found if task doesn't exist or not owned by user
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task
