"""empty message

Revision ID: e21f9e98d8c9
Revises: 001_initial, 65b49501b1a2
Create Date: 2026-03-09 15:07:55.019901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e21f9e98d8c9'
down_revision: Union[str, None] = ('001_initial', '65b49501b1a2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
