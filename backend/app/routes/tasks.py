"""Task management API routes."""
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from ..auth.dependencies import get_current_user
from ..database import get_session
from ..models.user import User
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate, TaskPublic
from ..utils.validation import validate_user_access
from ..utils.task_helpers import get_task_or_404


router = APIRouter(prefix="/api", tags=["tasks"])


@router.post(
    "/{user_id}/tasks",
    response_model=TaskPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task"
)
async def create_task(
    user_id: UUID,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Task:
    """
    Create a new task for the authenticated user.

    - **user_id**: Must match authenticated user's ID
    - **title**: Task title (required, 1-255 characters)
    - **description**: Task description (optional, max 1000 characters)

    Returns the created task with generated ID and timestamps.
    """
    # Validate user has access to this route
    validate_user_access(user_id, current_user)

    # Create task with authenticated user as owner
    task = Task(
        user_id=current_user.user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False,
        priority=task_data.priority or "medium",
        due_date=task_data.due_date
    )

    # Save to database
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get(
    "/{user_id}/tasks",
    response_model=List[TaskPublic],
    summary="Get all tasks for user"
)
async def list_tasks(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> List[Task]:
    """
    Retrieve all tasks for the authenticated user.

    - **user_id**: Must match authenticated user's ID

    Returns list of tasks ordered by creation date (newest first).
    Returns empty list if user has no tasks.
    """
    # Validate user has access to this route
    validate_user_access(user_id, current_user)

    # Query tasks filtered by user_id, ordered by created_at descending
    statement = select(Task).where(
        Task.user_id == current_user.user_id
    ).order_by(Task.created_at.desc())

    tasks = session.exec(statement).all()

    return list(tasks)


@router.get(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskPublic,
    summary="Get a specific task"
)
async def get_task(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Task:
    """
    Retrieve a specific task by ID.

    - **user_id**: Must match authenticated user's ID
    - **task_id**: Task ID to retrieve

    Returns 404 if task doesn't exist or belongs to another user.
    """
    # Validate user has access to this route
    validate_user_access(user_id, current_user)

    # Get task with ownership verification
    task = get_task_or_404(task_id, current_user.user_id, session)

    return task


@router.put(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskPublic,
    summary="Update a task"
)
async def update_task(
    user_id: UUID,
    task_id: UUID,
    update_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Task:
    """
    Update a task's title, description, or completion status.

    - **user_id**: Must match authenticated user's ID
    - **task_id**: Task ID to update
    - **title**: New title (optional)
    - **description**: New description (optional)
    - **completed**: New completion status (optional)

    Only provided fields are updated. Omitted fields remain unchanged.
    Returns 404 if task doesn't exist or belongs to another user.
    """
    # Validate user has access to this route
    validate_user_access(user_id, current_user)

    # Get task with ownership verification
    task = get_task_or_404(task_id, current_user.user_id, session)

    # Update only provided fields
    if update_data.title is not None:
        task.title = update_data.title
    if update_data.description is not None:
        task.description = update_data.description
    if update_data.completed is not None:
        task.completed = update_data.completed
    if update_data.priority is not None:
        task.priority = update_data.priority
    if update_data.due_date is not None:
        task.due_date = update_data.due_date

    # Save changes
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.patch(
    "/{user_id}/tasks/{task_id}/complete",
    response_model=TaskPublic,
    summary="Toggle task completion status"
)
async def toggle_task_completion(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Task:
    """
    Toggle a task's completion status (false → true, true → false).

    - **user_id**: Must match authenticated user's ID
    - **task_id**: Task ID to toggle

    Returns 404 if task doesn't exist or belongs to another user.
    """
    # Validate user has access to this route
    validate_user_access(user_id, current_user)

    # Get task with ownership verification
    task = get_task_or_404(task_id, current_user.user_id, session)

    # Toggle completion status
    task.completed = not task.completed

    # Save changes
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete(
    "/{user_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task"
)
async def delete_task(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> None:
    """
    Permanently delete a task.

    - **user_id**: Must match authenticated user's ID
    - **task_id**: Task ID to delete

    Returns 204 No Content on success.
    Returns 404 if task doesn't exist or belongs to another user.
    """
    # Validate user has access to this route
    validate_user_access(user_id, current_user)

    # Get task with ownership verification
    task = get_task_or_404(task_id, current_user.user_id, session)

    # Delete task
    session.delete(task)
    session.commit()
