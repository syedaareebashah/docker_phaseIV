from typing import List, Dict, Any
from datetime import datetime
from uuid import UUID
from ..models.task import Task, TaskStatus, TaskPriority
from ..database.session import get_session
from sqlmodel import Session, select

class TaskService:
    def __init__(self):
        pass

    def add_task(self, user_id: str, content: str, priority: str = "medium", due_date: str = None) -> Dict[str, Any]:
        """Add a new task for a user."""
        with get_session() as session:
            # Convert priority string to enum
            try:
                priority_enum = TaskPriority[priority.upper()]
            except KeyError:
                priority_enum = TaskPriority.MEDIUM
            
            # Create new task
            task = Task(
                user_id=UUID(user_id),
                title=content,
                description=content,  # Using content as description for simplicity
                completed=False,
                priority=priority_enum,
                due_date=due_date
            )
            
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return {
                "id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority.value,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }

    def list_tasks(self, user_id: str, filter_type: str = "all", sort_by: str = "created_at", 
                   sort_order: str = "desc", limit: int = 10) -> List[Dict[str, Any]]:
        """List tasks for a user with filters and sorting."""
        with get_session() as session:
            # Build query
            query = select(Task).where(Task.user_id == UUID(user_id))
            
            # Apply filters
            if filter_type == "pending":
                query = query.where(Task.completed == False)
            elif filter_type == "completed":
                query = query.where(Task.completed == True)
            elif filter_type == "overdue":
                # Note: This is a simplified check - in a real app, you'd compare with current date
                query = query.where(Task.due_date < str(datetime.now()))
            
            # Apply sorting
            if sort_by == "created_at":
                if sort_order == "desc":
                    query = query.order_by(Task.created_at.desc())
                else:
                    query = query.order_by(Task.created_at.asc())
            elif sort_by == "due_date":
                if sort_order == "desc":
                    query = query.order_by(Task.due_date.desc())
                else:
                    query = query.order_by(Task.due_date.asc())
            elif sort_by == "priority":
                if sort_order == "desc":
                    query = query.order_by(Task.priority.desc())
                else:
                    query = query.order_by(Task.priority.asc())
            
            # Apply limit
            query = query.limit(limit)
            
            tasks = session.exec(query).all()
            
            return [{
                "id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority.value,
                "due_date": task.due_date,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            } for task in tasks]

    def complete_task(self, user_id: str, task_id: int) -> Dict[str, Any]:
        """Mark a task as completed."""
        with get_session() as session:
            # Find the task
            task = session.get(Task, UUID(task_id)) if self._is_valid_uuid(task_id) else None
            
            if not task:
                # If task_id is not a UUID, try to find by integer ID (if stored differently)
                # This is a fallback - in a real implementation, you'd handle this properly
                from sqlmodel import func
                # Assuming task_id is the UUID string representation
                task = session.get(Task, task_id)
            
            if not task:
                raise ValueError(f"Task with id {task_id} not found")
            
            # Verify that the task belongs to the user
            if str(task.user_id) != user_id:
                raise PermissionError("Task does not belong to user")
            
            # Update task
            task.completed = True
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return {
                "id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            }

    def delete_task(self, user_id: str, task_id: int) -> Dict[str, Any]:
        """Delete a task."""
        with get_session() as session:
            # Find the task
            task = session.get(Task, UUID(task_id)) if self._is_valid_uuid(task_id) else None
            
            if not task:
                task = session.get(Task, task_id)
            
            if not task:
                raise ValueError(f"Task with id {task_id} not found")
            
            # Verify that the task belongs to the user
            if str(task.user_id) != user_id:
                raise PermissionError("Task does not belong to user")
            
            # Delete task
            session.delete(task)
            session.commit()
            
            return {
                "id": str(task.id),
                "deleted": True
            }

    def update_task(self, user_id: str, task_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task."""
        with get_session() as session:
            # Find the task
            task = session.get(Task, UUID(task_id)) if self._is_valid_uuid(task_id) else None
            
            if not task:
                task = session.get(Task, task_id)
            
            if not task:
                raise ValueError(f"Task with id {task_id} not found")
            
            # Verify that the task belongs to the user
            if str(task.user_id) != user_id:
                raise PermissionError("Task does not belong to user")
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(task, key):
                    if key == 'priority':
                        try:
                            value = TaskPriority[value.upper()]
                        except KeyError:
                            # If invalid priority, skip or use default
                            continue
                    setattr(task, key, value)
            
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return {
                "id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority.value,
                "updated_at": task.updated_at.isoformat()
            }

    def _is_valid_uuid(self, val):
        """Check if a value is a valid UUID."""
        try:
            UUID(str(val))
            return True
        except ValueError:
            return False