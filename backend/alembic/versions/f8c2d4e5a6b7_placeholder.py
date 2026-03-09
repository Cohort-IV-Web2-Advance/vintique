"""placeholder

Revision ID: f8c2d4e5a6b7
Revises: <whatever the revision before it was>
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'f8c2d4e5a6b7'
down_revision = None  # or the actual parent revision ID
branch_labels = None
depends_on = None

def upgrade():
    pass  # already applied, or never needed

def downgrade():
    pass