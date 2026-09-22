"""block deleted auth sessions

Revision ID: a71c3f42d2e8
Revises: f3e9c1a27b44
Create Date: 2026-09-22
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a71c3f42d2e8"
down_revision: Union[str, Sequence[str], None] = "f3e9c1a27b44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "deletedauthuser",
        sa.Column("auth_user_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("auth_user_id"),
    )

def downgrade() -> None:
    op.drop_table("deletedauthuser")
