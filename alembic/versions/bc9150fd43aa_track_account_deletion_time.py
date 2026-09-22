"""track account deletion time

Revision ID: bc9150fd43aa
Revises: a71c3f42d2e8
Create Date: 2026-09-22
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "bc9150fd43aa"
down_revision: Union[str, Sequence[str], None] = "a71c3f42d2e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        "deletedauthuser",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

def downgrade() -> None:
    op.drop_column("deletedauthuser", "deleted_at")
