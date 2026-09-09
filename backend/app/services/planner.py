from fastapi import HTTPException
from sqlmodel import Session
from ..database import engine
from ..backend_models.character_recipe import character_recipes
from ..dtos import CharacterPlanItem
from .base import BaseService
from .characters import CharacterService
from .recipes import RecipeService
from .settings import SettingsService

class PlannerService(BaseService):
    character_service = CharacterService()
    recipe_service = RecipeService()
    settings_service = SettingsService()

    def __init__(self, engine_override=None):
        self.engine = engine_override or engine

    def get_options(self, character_id: int):
        with Session(self.engine) as session:
            character = self.character_service.get(session, character_id)

            if character is None:
                raise HTTPException(status_code=404, detail="Character not found")

            settings = self.settings_service.get_current(session)

            if settings is None:
                raise HTTPException(status_code=400, detail="Select an expansion before planning")

            assignments = character_recipes.get_current(
                session,
                character,
                settings.current_expansion_id,
            )

            options = []

            for assignment in assignments:
                recipe = self.recipe_service.get(session, assignment.recipe_id)

                if recipe is None:
                    raise HTTPException(status_code=404, detail="Recipe not found")

                if assignment.concentration_cost <= 0:
                    raise HTTPException(status_code=400, detail="Invalid concentration cost")

                max_possible = character.concentration // assignment.concentration_cost
                option = {
                    "recipe_id": recipe.id,
                    "recipe_name": recipe.name,
                    "profession_id": recipe.profession_id,
                    "concentration_cost": assignment.concentration_cost,
                    "max_possible": max_possible,
                }
                options.append(option)

            return options

    def calculate_plan(self, plan: list[CharacterPlanItem]):
        with Session(self.engine) as session:
            ingredient_totals = {}
            concentration_used = {}

            settings = self.settings_service.get_current(session)

            if settings is None:
                raise HTTPException(status_code=400, detail="Select an expansion before planning")

            for item in plan:
                character = self.character_service.get(session, item.character_id)

                if character is None:
                    raise HTTPException(status_code=404, detail="Character not found")

                assignment = character_recipes.get_by_character_recipe(
                    session,
                    item.character_id,
                    item.recipe_id,
                )

                if assignment is None:
                    raise HTTPException(status_code=400, detail="Character does not know this recipe")

                recipe = self.recipe_service.get_with_ingredients(session, item.recipe_id)

                if recipe is None:
                    raise HTTPException(status_code=404, detail="Recipe not found")

                if recipe.profession_id not in (character.profession1_id, character.profession2_id):
                    raise HTTPException(status_code=400, detail="Recipe does not belong to either active profession")

                if recipe.expansion_id != settings.current_expansion_id:
                    raise HTTPException(status_code=400, detail="Recipe does not belong to the selected expansion")

                if assignment.concentration_cost <= 0:
                    raise HTTPException(status_code=400, detail="Invalid concentration cost")

                cost = item.crafts * assignment.concentration_cost
                budget_key = (item.character_id, recipe.profession_id)
                previously_used = concentration_used.get(budget_key, 0)
                total_used = previously_used + cost

                if total_used > character.concentration:
                    raise HTTPException(status_code=400, detail="Not enough concentration")

                concentration_used[budget_key] = total_used

                for link in recipe.ingredients:
                    name = link.ingredient.name
                    amount = link.amount_required * item.crafts
                    ingredient_totals[name] = ingredient_totals.get(name, 0) + amount

            return ingredient_totals