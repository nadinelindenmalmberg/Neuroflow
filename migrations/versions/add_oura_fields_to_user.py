"""Add Oura API token fields to User model

Revision ID: add_oura_fields_to_user
Revises: 31fad8577e40
Create Date: 2025-07-26 11:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_oura_fields_to_user'
down_revision = 'create_user_table'
branch_labels = None
depends_on = None


def upgrade():
    # Add Oura API token fields to User table
    op.add_column('user', sa.Column('oura_api_token', sa.String(length=500), nullable=True))
    op.add_column('user', sa.Column('last_oura_sync', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('sync_frequency', sa.String(length=20), nullable=True, server_default='manual'))
    op.add_column('user', sa.Column('selected_dashboard_metrics', sa.Text(), nullable=True))


def downgrade():
    # Remove Oura API token fields from User table
    op.drop_column('user', 'selected_dashboard_metrics')
    op.drop_column('user', 'sync_frequency')
    op.drop_column('user', 'last_oura_sync')
    op.drop_column('user', 'oura_api_token') 