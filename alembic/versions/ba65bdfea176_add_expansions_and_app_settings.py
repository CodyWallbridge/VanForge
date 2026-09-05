"""add expansions and app settings

Revision ID: ba65bdfea176
Revises: 237c47c308e4
Create Date: 2026-09-05 00:43:06.853865

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'ba65bdfea176'
down_revision: Union[str, Sequence[str], None] = '237c47c308e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "expansion",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "appsettings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("current_expansion_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["current_expansion_id"], ["expansion.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute(
        "INSERT INTO expansion (id, name) VALUES (1, 'Midnight')"
    )
    op.execute(
        "INSERT INTO appsettings (id, current_expansion_id) VALUES (1, 1)"
    )

    op.add_column(
        "recipe",
        sa.Column("expansion_id", sa.Integer(), nullable=True),
    )
    op.execute(
        "UPDATE recipe SET expansion_id = 1"
    )

    with op.batch_alter_table("recipe") as batch_op:
        batch_op.alter_column(
            "expansion_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.create_foreign_key(
            "fk_recipe_expansion_id",
            "expansion",
            ["expansion_id"],
            ["id"],
        )

def downgrade() -> None:
    with op.batch_alter_table("recipe") as batch_op:
        batch_op.drop_constraint(
            "fk_recipe_expansion_id",
            type_="foreignkey",
        )
        batch_op.drop_column("expansion_id")

    op.drop_table("appsettings")
    op.drop_table("expansion")