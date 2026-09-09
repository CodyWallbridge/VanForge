from sqlmodel import Session
from ..database import engine
from ..backend_models.ingredient import ingredients
from ..models import Ingredient
from ..dtos import IngredientCreate
from ..utils.validation import clean_name
from .base import BaseService

class IngredientService(BaseService):
    model_class = Ingredient
    data_accessor = ingredients

    def __init__(self, engine_override=None):
        self.engine = engine_override or engine

    def create_ingredient(self, ingredient_data: IngredientCreate):
        with Session(self.engine) as session:
            name = clean_name(ingredient_data.name)
            existing = self.data_accessor.get_by_name(session, name)

            if existing is not None:
                return existing

            ingredient = Ingredient(name=name)
            ingredient = self.create(entity=ingredient, session=session)

            session.commit()
            session.refresh(ingredient)

            return ingredient

    def get_ingredients(self, search: str | None = None):
        with Session(self.engine) as session:
            return self.data_accessor.search(session, search)

    def get_by_name(
        self,
        session: Session,
        name: str,
    ):
        return self.data_accessor.get_by_name(session, name)