"""Cascade character assignments and recipe links on parent deletion."""
from alembic import op

revision = "c82a19d740ef"
down_revision = "ba65bdfea176"
branch_labels = None
depends_on = None

# Assign names to existing unnamed SQLite foreign keys during reflection.
NAMING_CONVENTION = {"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"}

def upgrade() -> None:
    with op.batch_alter_table("characterrecipe", naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.drop_constraint("fk_characterrecipe_character_id_character", type_="foreignkey")
        batch_op.drop_constraint("fk_characterrecipe_recipe_id_recipe", type_="foreignkey")

        batch_op.create_foreign_key(
            "fk_characterrecipe_character_id_character",
            "character",
            ["character_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.create_foreign_key(
            "fk_characterrecipe_recipe_id_recipe",
            "recipe",
            ["recipe_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("recipeingredient", naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.drop_constraint("fk_recipeingredient_recipe_id_recipe", type_="foreignkey")

        batch_op.create_foreign_key(
            "fk_recipeingredient_recipe_id_recipe",
            "recipe",
            ["recipe_id"],
            ["id"],
            ondelete="CASCADE",
        )

def downgrade() -> None:
    with op.batch_alter_table("recipeingredient", naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.drop_constraint("fk_recipeingredient_recipe_id_recipe", type_="foreignkey")

        batch_op.create_foreign_key(
            "fk_recipeingredient_recipe_id_recipe",
            "recipe",
            ["recipe_id"],
            ["id"],
        )

    with op.batch_alter_table("characterrecipe", naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.drop_constraint("fk_characterrecipe_character_id_character", type_="foreignkey")
        batch_op.drop_constraint("fk_characterrecipe_recipe_id_recipe", type_="foreignkey")

        batch_op.create_foreign_key(
            "fk_characterrecipe_character_id_character",
            "character",
            ["character_id"],
            ["id"],
        )
        batch_op.create_foreign_key(
            "fk_characterrecipe_recipe_id_recipe",
            "recipe",
            ["recipe_id"],
            ["id"],
        )
