from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import Dict, Any, Optional
import json
from pydantic import BaseModel

from ..models.user import User
from ..models.message import MessageCreate, MessageResponse
from ..middleware.auth import get_current_user
from ..agents.todo_agent import TodoAgent
from ..database.session import get_session
from ..models.conversation import Conversation
from ..models.message import Message

router = APIRouter(prefix="/api", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    tool_calls: Optional[list] = []

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db_session=Depends(get_session)
):
    """
    Main chat endpoint for the AI assistant.
    
    Accepts a user message and returns an AI response with potential tool calls.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User ID mismatch"
        )
    
    try:
        # Create or retrieve conversation
        conversation_id = request.conversation_id
        if not conversation_id:
            # Create a new conversation
            conversation = Conversation(user_id=user_id)
            db_session.add(conversation)
            db_session.commit()
            db_session.refresh(conversation)
            conversation_id = str(conversation.id)
        else:
            # Verify conversation belongs to user
            conversation = db_session.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        
        # Create user message in database
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )
        db_session.add(user_message)
        db_session.commit()
        
        # Process with AI agent
        agent = TodoAgent()
        result = agent.process_message(
            user_id=str(user_id),
            message=request.message,
            conversation_id=conversation_id
        )
        
        # Create assistant message in database
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=result.get('response', ''),
            tool_calls=result.get('tool_calls', [])
        )
        db_session.add(assistant_message)
        db_session.commit()
        
        return ChatResponse(
            response=result.get('response', ''),
            conversation_id=conversation_id,
            tool_calls=result.get('tool_calls', [])
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.get("/{user_id}/conversations")
async def list_conversations(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db_session=Depends(get_session)
):
    """
    List all conversations for a user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User ID mismatch"
        )
    
    conversations = db_session.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(Conversation.created_at.desc()).all()
    
    return [{"id": str(conv.id), "created_at": conv.created_at} for conv in conversations]