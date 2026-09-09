from fastapi import HTTPException
from sqlmodel import Session
from ..backend_models.recipe_ingredient import recipe_ingredients
from ..models import Ingredient, RecipeIngredient
from ..dtos import RecipeIngredientCreate
from ..utils.validation import clean_name
from .base import BaseService
from .ingredients import IngredientService

class RecipeIngredientService(BaseService):
    model_class = RecipeIngredient
    data_accessor = recipe_ingredients
    ingredient_service = IngredientService()

    def resolve_ingredients(
        self,
        entries: list[RecipeIngredientCreate],
        session: Session,
    ):
        resolved = []
        seen_ids = set()
        seen_names = set()

        for entry in entries:
            if entry.ingredient_id is not None:
                ingredient = self.ingredient_service.get(session, entry.ingredient_id)

                if ingredient is None:
                    raise HTTPException(status_code=404, detail="Ingredient not found")

                name = ingredient.name.strip()
            else:
                name = clean_name(entry.name)
                ingredient = self.ingredient_service.get_by_name(session, name)

            key = name.casefold()

            if key in seen_names or (ingredient is not None and ingredient.id in seen_ids):
                raise HTTPException(status_code=400, detail="Each ingredient can only appear once in a recipe")

            seen_names.add(key)

            if ingredient is not None:
                seen_ids.add(ingredient.id)

            resolved_entry = (ingredient, name, entry.amount_required)
            resolved.append(resolved_entry)

        return resolved

    def add_ingredient_links(
        self,
        recipe_id: int,
        resolved,
        session: Session,
    ):
        for ingredient, name, amount in resolved:
            if ingredient is None:
                ingredient = Ingredient(name=name)
                ingredient = self.ingredient_service.create(entity=ingredient, session=session)

            link = RecipeIngredient(
                recipe_id=recipe_id,
                ingredient_id=ingredient.id,
                amount_required=amount,
            )
            self.create(entity=link, session=session)

    def delete_for_recipe(
        self,
        session: Session,
        recipe_id: int,
    ):
        self.data_accessor.delete_for_recipe(session, recipe_id)
