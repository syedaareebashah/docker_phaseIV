"""Validation utilities for user access control."""
from uuid import UUID
from fastapi import HTTPException, status

from ..models.user import User


def validate_user_access(route_user_id: UUID, current_user: User) -> None:
    """
    Validate that the route user_id matches the authenticated user.

    Args:
        route_user_id: User ID from the route path parameter
        current_user: Authenticated user from JWT token

    Raises:
        HTTPException: 403 Forbidden if user IDs don't match
    """
    if route_user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: cannot access other users' resources"
        )
