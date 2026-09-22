"""add account recipe profits

Revision ID: f3e9c1a27b44
Revises: 8ab39eaf99cb
Create Date: 2026-09-21
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "f3e9c1a27b44"
down_revision: Union[str, Sequence[str], None] = "8ab39eaf99cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "recipeprofit",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("profit_per_craft", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["account.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipe.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id", "recipe_id", name="uq_recipeprofit_account_recipe"),
    )

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            INSERT INTO recipeprofit (account_id, recipe_id, profit_per_craft)
            SELECT account.id, recipe.id, recipe.profit_per_craft
            FROM account
            CROSS JOIN recipe
            """
        ),
    )

    op.drop_column("recipe", "profit_per_craft")

def downgrade() -> None:
    op.add_column(
        "recipe",
        sa.Column("profit_per_craft", sa.Integer(), nullable=False, server_default="0"),
    )

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE recipe
            SET profit_per_craft = recipeprofit.profit_per_craft
            FROM recipeprofit
            WHERE recipeprofit.recipe_id = recipe.id
              AND recipeprofit.account_id = (
                  SELECT id
                  FROM account
                  WHERE role = 'admin'
                  ORDER BY id
                  LIMIT 1
              )
            """
        ),
    )

    op.drop_table("recipeprofit")
