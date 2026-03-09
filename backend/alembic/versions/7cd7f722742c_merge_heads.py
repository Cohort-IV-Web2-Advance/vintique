"""merge heads

Revision ID: 7cd7f722742c
Revises: e21f9e98d8c9
Create Date: 2026-03-09 15:08:46.804605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cd7f722742c'
down_revision: Union[str, None] = 'e21f9e98d8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
