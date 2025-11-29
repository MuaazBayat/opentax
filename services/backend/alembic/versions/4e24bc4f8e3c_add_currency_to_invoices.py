"""add_currency_to_invoices

Revision ID: 4e24bc4f8e3c
Revises: 64dfd7b27dce
Create Date: 2025-11-28 20:53:35.576064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e24bc4f8e3c'
down_revision: Union[str, Sequence[str], None] = '64dfd7b27dce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add currency column to invoices table
    op.add_column('invoices', sa.Column('currency', sa.String(), nullable=True))
    # Set default value for existing rows
    op.execute("UPDATE invoices SET currency = 'USD' WHERE currency IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    # Remove currency column from invoices table
    op.drop_column('invoices', 'currency')
