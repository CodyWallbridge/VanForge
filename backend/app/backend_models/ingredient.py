from sqlmodel import Session, select
from ..models import Ingredient
from .base import CRUDBase

class IngredientCRUD(CRUDBase[Ingredient]):

    def get_by_name(
        self,
        session: Session,
        name: str,
    ):
        key = name.strip().casefold()
        ingredients = self.get_all(session)

        for ingredient in ingredients:
            if ingredient.name.strip().casefold() == key:
                return ingredient

        return None

    def search(self, session: Session, search=None):
        ingredients = session.exec(
            select(Ingredient)
            .order_by(Ingredient.name, Ingredient.id)
        ).all()

        if search is None:
            return ingredients

        key = search.strip().casefold()
        return [
            ingredient
            for ingredient in ingredients
            if key in ingredient.name.casefold()
        ]

ingredients = IngredientCRUD(Ingredient)