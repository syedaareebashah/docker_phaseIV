from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.user_id")  # Assuming user table exists
    title: Optional[str] = Field(default=None, max_length=255)  # Optional title for the conversation
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id")
    role: str = Field(sa_column_kwargs={"check": "role IN ('user', 'assistant', 'system')"})  # user, assistant, or system
    content: str = Field()  # The actual message content
    tool_calls: Optional[List] = Field(default=None)  # Optional list of tool calls made
    created_at: datetime = Field(default_factory=datetime.utcnow)