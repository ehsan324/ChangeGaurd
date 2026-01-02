"""add environment to changes

Revision ID: 647efb88ca2e
Revises: 29d24865d8d9
Create Date: 2026-01-02 10:31:43.790834

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '647efb88ca2e'
down_revision: Union[str, Sequence[str], None] = '29d24865d8d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("changes", sa.Column("environment", sa.String(length=32), nullable=False))

def downgrade() -> None:
    op.drop_column("changes", "environment")