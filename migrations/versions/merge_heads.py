"""Merge multiple heads

Revision ID: merge_heads
Revises: 31fad8577e40, add_sync_logs_table
Create Date: 2025-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_heads'
down_revision = ('31fad8577e40', 'add_sync_logs_table')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

