"""Add IDs to link tables while preserving unique pairs and cascade rules."""
from alembic import op
import sqlalchemy as sa

revision = "d391f06a2b84"
down_revision = "c82a19d740ef"
branch_labels = None
depends_on = None

NAMING_CONVENTION = {"pk": "pk_%(table_name)s"}

def upgrade() -> None:
    op.add_column("characterrecipe", sa.Column("id", sa.Integer(), nullable=True))
    op.add_column("recipeingredient", sa.Column("id", sa.Integer(), nullable=True))

    # Existing SQLite rowids provide a unique ID for every saved link.
    op.execute("UPDATE characterrecipe SET id = rowid")
    op.execute("UPDATE recipeingredient SET id = rowid")

    with op.batch_alter_table("characterrecipe", naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.drop_constraint("pk_characterrecipe", type_="primary")
        batch_op.alter_column(
            "id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.create_primary_key("pk_characterrecipe", ["id"])
        batch_op.create_unique_constraint("uq_characterrecipe_character_recipe", ["character_id", "recipe_id"])

    with op.batch_alter_table("recipeingredient", naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.drop_constraint("pk_recipeingredient", type_="primary")
        batch_op.alter_column(
            "id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.create_primary_key("pk_recipeingredient", ["id"])
        batch_op.create_unique_constraint("uq_recipeingredient_recipe_ingredient", ["recipe_id", "ingredient_id"])

def downgrade() -> None:
    with op.batch_alter_table("recipeingredient", naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.drop_constraint("uq_recipeingredient_recipe_ingredient", type_="unique")
        batch_op.drop_constraint("pk_recipeingredient", type_="primary")
        batch_op.create_primary_key("pk_recipeingredient", ["recipe_id", "ingredient_id"])
        batch_op.drop_column("id")

    with op.batch_alter_table("characterrecipe", naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.drop_constraint("uq_characterrecipe_character_recipe", type_="unique")
        batch_op.drop_constraint("pk_characterrecipe", type_="primary")
        batch_op.create_primary_key("pk_characterrecipe", ["character_id", "recipe_id"])
        batch_op.drop_column("id")
