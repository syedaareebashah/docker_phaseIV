---
name: database-skill
description: Design database schemas, create tables, write migrations, and optimize queries. Use for database architecture and data modeling.
---

# Database Skill – Create tables, migrations, schema design

## Instructions

1. **Schema Design**
   - Identify entities and relationships
   - Define primary and foreign keys
   - Choose appropriate data types
   - Normalize data structure (avoid redundancy)

2. **Table Creation**
   - Use SQLModel for ORM models
   - Define fields with proper constraints
   - Add indexes for frequently queried columns
   - Set up timestamps (created_at, updated_at)

3. **Migrations**
   - Use Alembic for database migrations
   - Create incremental migration files
   - Write both upgrade and downgrade functions
   - Test migrations before applying to production

4. **Relationships**
   - Define one-to-many relationships
   - Set up foreign key constraints
   - Configure cascade delete behavior
   - Implement many-to-many with junction tables

## Best Practices

- Always use UUID for primary keys (better security and distribution)
- Index foreign keys and frequently queried fields
- Use NOT NULL constraints where appropriate
- Add unique constraints for fields like email
- Use appropriate data types (VARCHAR vs TEXT, INT vs BIGINT)
- Include created_at and updated_at timestamps
- Document schema decisions with comments
- Plan for data growth and scalability

## Example Structure
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    tasks: list["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        index=True,
        nullable=False
    )
    title: str = Field(max_length=200)
    description: str | None = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    user: User = Relationship(back_populates="tasks")
```

## Migration Example
```python
"""create users and tasks tables

Revision ID: 001
Create Date: 2024-01-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])

def downgrade():
    op.drop_table('tasks')
    op.drop_table('users')
```

## Query Optimization

- Use SELECT with specific columns, not SELECT *
- Add WHERE clauses to filter early
- Use LIMIT for pagination
- Create compound indexes for multi-column queries
- Use EXPLAIN to analyze query performance

## Database Connection
```python
from sqlmodel import create_engine, Session
from sqlalchemy.pool import NullPool

# Neon Serverless PostgreSQL connection
DATABASE_URL = "postgresql://user:password@host/database"

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    poolclass=NullPool  # For serverless environments
)

def get_session():
    with Session(engine) as session:
        yield session
```

## When to Use This Skill

- Designing new database schemas
- Creating SQLModel table models
- Writing database migrations
- Setting up relationships between tables
- Optimizing database queries
- Configuring database connections
- Adding indexes for performance
- Refactoring existing schemas