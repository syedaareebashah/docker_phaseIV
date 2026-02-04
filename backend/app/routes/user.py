from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlmodel import Session
from ..database import get_session
from ..models.user import User
from ..auth.dependencies import get_current_user
from ..schemas.user import UserPublic

router = APIRouter(prefix="/api", tags=["User"])

@router.get("/{user_id}/profile", response_model=UserPublic)
async def get_user_profile(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get user profile (demonstrates user isolation pattern).

    Args:
        user_id: User ID from path parameter
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        UserPublic: User profile information

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
    """
    # Enforce user isolation - users can only access their own profile
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )

    # Return user profile
    return UserPublic(
        user_id=current_user.user_id,
        email=current_user.email,
        created_at=current_user.created_at
    )
