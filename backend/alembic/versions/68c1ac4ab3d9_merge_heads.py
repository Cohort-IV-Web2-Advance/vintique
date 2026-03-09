"""merge heads

Revision ID: 68c1ac4ab3d9
Revises: 7cd7f722742c
Create Date: 2026-03-09 15:09:06.505750

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68c1ac4ab3d9'
down_revision: Union[str, None] = '7cd7f722742c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
