from sqlmodel import create_engine, Session, select
from typing import Generator
from contextlib import contextmanager
import os
from ..models.user import User
from ..models.task import Task
from ..models.conversation import Conversation, Message

# Get database URL from environment, default to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_chatbot.db")

engine = create_engine(DATABASE_URL, echo=True)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def init_db():
    """Initialize the database and create tables."""
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)