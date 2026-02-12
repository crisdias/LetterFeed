"""add auto_extract_content to settings

Revision ID: 421792d28d15
Revises: 75ed3dbf1e16
Create Date: 2026-02-12 11:52:12.796250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '421792d28d15'
down_revision: Union[str, Sequence[str], None] = '75ed3dbf1e16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add auto_extract_content column to settings table
    op.add_column('settings', sa.Column('auto_extract_content', sa.Boolean(), nullable=True))
    # Set default value for existing rows
    op.execute("UPDATE settings SET auto_extract_content = 1")
    # Make column non-nullable
    with op.batch_alter_table('settings') as batch_op:
        batch_op.alter_column('auto_extract_content', nullable=False, server_default=sa.true())


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('settings', 'auto_extract_content')
