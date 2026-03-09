"""remove payment_id from transactions

Revision ID: 65b49501b1a2
Revises: 72440580f513
Create Date: 2026-03-08 10:22:25.779787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '65b49501b1a2'
down_revision: Union[str, None] = '72440580f513'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass  # payment_id was never in 001_initial

def downgrade() -> None:
    pass
