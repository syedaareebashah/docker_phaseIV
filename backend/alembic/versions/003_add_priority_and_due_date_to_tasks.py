"""Add priority and due_date to tasks table

Revision ID: 003
Revises: 002_create_tasks_table
Create Date: 2026-02-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002_create_tasks_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add priority column with default value 'medium'
    op.add_column('tasks', sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium'))

    # Add due_date column
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove due_date column
    op.drop_column('tasks', 'due_date')

    # Remove priority column
    op.drop_column('tasks', 'priority')