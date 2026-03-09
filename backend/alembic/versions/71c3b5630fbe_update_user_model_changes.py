"""Update user model changes

Revision ID: 71c3b5630fbe
Revises: 68c1ac4ab3d9
Create Date: 2026-03-09 18:51:31.020063
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision: str = '71c3b5630fbe'
down_revision: Union[str, None] = '68c1ac4ab3d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Handle cart foreign key
    try:
        op.drop_constraint('cart_ibfk_1', 'cart', type_='foreignkey')
    except:
        pass

    try:
        op.alter_column(
            'cart',
            'product_id',
            existing_type=mysql.INTEGER(),
            nullable=False
        )
    except:
        pass

    try:
        op.create_foreign_key(None, 'cart', 'products', ['product_id'], ['id'])
    except:
        pass


    # Guest indexes
    try:
        op.drop_index('guest_id', table_name='guests')
    except:
        pass

    try:
        op.drop_index('ix_guests_guest_id', table_name='guests')
    except:
        pass

    op.create_index(op.f('ix_guests_guest_id'), 'guests', ['guest_id'], unique=True)


    # Orders table updates
    # product_id already exists so we DO NOT add it again

    op.add_column('orders', sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False))
    op.add_column('orders', sa.Column('quantity', sa.Integer(), nullable=False))
    op.add_column('orders', sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False))
    op.add_column('orders', sa.Column('order_status', sa.String(length=50), nullable=False))
    op.add_column('orders', sa.Column('shipping_address', sa.String(length=500), nullable=True))

    try:
        op.create_foreign_key(None, 'orders', 'products', ['product_id'], ['id'])
    except:
        pass

    try:
        op.drop_column('orders', 'total_amount')
    except:
        pass

    try:
        op.drop_column('orders', 'status')
    except:
        pass


    # Transactions table updates
    try:
        op.alter_column(
            'transactions',
            'order_id',
            existing_type=mysql.INTEGER(),
            nullable=False
        )
    except:
        pass

    try:
        op.alter_column(
            'transactions',
            'amount',
            existing_type=mysql.DECIMAL(precision=10, scale=2),
            nullable=True
        )
    except:
        pass

    try:
        op.drop_constraint('transactions_ibfk_2', 'transactions', type_='foreignkey')
    except:
        pass

    try:
        op.drop_column('transactions', 'transaction_type')
    except:
        pass

    try:
        op.drop_column('transactions', 'user_id')
    except:
        pass


    # Users table indexes
    try:
        op.drop_index('email', table_name='users')
    except:
        pass

    try:
        op.drop_index('username', table_name='users')
    except:
        pass

    try:
        op.drop_index('ix_users_email', table_name='users')
    except:
        pass

    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    try:
        op.drop_index('ix_users_username', table_name='users')
    except:
        pass

    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)


def downgrade() -> None:
    pass