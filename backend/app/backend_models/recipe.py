from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from ..models import Recipe, RecipeIngredient
from .base import CRUDBase

class RecipeCRUD(CRUDBase[Recipe]):
    def get_with_ingredients(self, session: Session, recipe_id):
        recipe = session.exec(
            select(Recipe).options(
                selectinload(Recipe.ingredients)
                .selectinload(RecipeIngredient.ingredient),
            ).where(Recipe.id == recipe_id).execution_options(populate_existing=True),
        ).first()

        return recipe

    def get_filtered(self, session: Session, expansion_id=None, profession_id=None):
        statement = select(Recipe).options(
            selectinload(Recipe.ingredients)
            .selectinload(RecipeIngredient.ingredient),
        )

        if expansion_id is not None:
            statement = statement.where(Recipe.expansion_id == expansion_id)

        if profession_id is not None:
            statement = statement.where(Recipe.profession_id == profession_id)

        return session.exec(
            statement.order_by(Recipe.id),
        ).all()

    def has_expansion(self, session: Session, expansion_id):
        recipe_id = session.exec(
            select(Recipe.id)
            .where(Recipe.expansion_id == expansion_id),
        ).first()

        return recipe_id is not None

recipes = RecipeCRUD(Recipe)