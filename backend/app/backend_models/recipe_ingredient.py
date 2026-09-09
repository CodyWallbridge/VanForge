from sqlmodel import Session, select, delete
from ..models import RecipeIngredient
from .base import CRUDBase

class RecipeIngredientCRUD(CRUDBase[RecipeIngredient]):
    def get_all(self, session: Session):
        return session.exec(
            select(RecipeIngredient)
            .order_by(RecipeIngredient.recipe_id, RecipeIngredient.ingredient_id),
        ).all()

    def delete_for_recipe(self, session: Session, recipe_id):
        session.exec(
            delete(RecipeIngredient)
            .where(RecipeIngredient.recipe_id == recipe_id),
        )

recipe_ingredients = RecipeIngredientCRUD(RecipeIngredient)