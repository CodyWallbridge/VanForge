"""scope characters and settings to accounts

Revision ID: 8ab39eaf99cb
Revises: 435c743c72c3
Create Date: 2026-09-21 18:15:46.313746

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '8ab39eaf99cb'
down_revision: Union[str, Sequence[str], None] = '435c743c72c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("appsettings", sa.Column("account_id", sa.Integer(), nullable=True))
    op.add_column("character", sa.Column("account_id", sa.Integer(), nullable=True))

    connection = op.get_bind()
    admin_account_id = connection.execute(
        sa.text(
            """
            SELECT id
            FROM account
            WHERE role = 'admin'
            ORDER BY id
            LIMIT 1
            """
        ),
    ).scalar_one_or_none()

    existing_record_count = connection.execute(
        sa.text(
            """
            SELECT
                (SELECT COUNT(*) FROM appsettings) +
                (SELECT COUNT(*) FROM "character")
            """
        ),
    ).scalar_one()

    if admin_account_id is None and existing_record_count > 0:
        raise RuntimeError("An admin account is required to migrate existing data")

    if admin_account_id is not None:
        connection.execute(
            sa.text("UPDATE appsettings SET account_id = :account_id"),
            {"account_id": admin_account_id},
        )
        connection.execute(
            sa.text('UPDATE "character" SET account_id = :account_id'),
            {"account_id": admin_account_id},
        )

    op.alter_column("appsettings", "account_id", nullable=False)
    op.alter_column("character", "account_id", nullable=False)

    op.create_foreign_key(
        "fk_appsettings_account_id",
        "appsettings",
        "account",
        ["account_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_appsettings_account_id",
        "appsettings",
        ["account_id"],
    )
    op.create_foreign_key(
        "fk_character_account_id",
        "character",
        "account",
        ["account_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###

def downgrade() -> None:
    op.drop_constraint("fk_character_account_id", "character", type_="foreignkey")
    op.drop_column("character", "account_id")
    op.drop_constraint("uq_appsettings_account_id", "appsettings", type_="unique")
    op.drop_constraint("fk_appsettings_account_id", "appsettings", type_="foreignkey")
    op.drop_column("appsettings", "account_id")
    # ### end Alembic commands ###
