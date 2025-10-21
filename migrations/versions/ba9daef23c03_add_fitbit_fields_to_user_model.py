"""Add Fitbit fields to User model

Revision ID: ba9daef23c03
Revises: merge_heads
Create Date: 2025-09-15 11:46:32.736682

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba9daef23c03'
down_revision = 'merge_heads'
branch_labels = None
depends_on = None


def upgrade():
    # Add Fitbit OAuth fields to user table
    op.add_column('user', sa.Column('fitbit_access_token', sa.String(500), nullable=True))
    op.add_column('user', sa.Column('fitbit_refresh_token', sa.String(500), nullable=True))
    op.add_column('user', sa.Column('fitbit_token_expires_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('fitbit_user_id', sa.String(100), nullable=True))
    op.add_column('user', sa.Column('last_fitbit_sync', sa.DateTime(), nullable=True))


def downgrade():
    # Remove Fitbit OAuth fields from user table
    op.drop_column('user', 'last_fitbit_sync')
    op.drop_column('user', 'fitbit_user_id')
    op.drop_column('user', 'fitbit_token_expires_at')
    op.drop_column('user', 'fitbit_refresh_token')
    op.drop_column('user', 'fitbit_access_token')
