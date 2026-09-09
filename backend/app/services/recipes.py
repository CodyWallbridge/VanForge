from fastapi import HTTPException
from sqlmodel import Session
from ..database import engine
from ..backend_models.recipe import recipes
from ..models import Recipe
from ..dtos import RecipeCreate, RecipeProfitUpdate, RecipeUpdate
from ..utils.validation import clean_name
from .base import BaseService
from .professions import ProfessionService
from .recipe_ingredients import RecipeIngredientService

class RecipeService(BaseService):
    model_class = Recipe
    data_accessor = recipes
    profession_service = ProfessionService()
    recipe_ingredient_service = RecipeIngredientService()

    def __init__(self, engine_override=None):
        self.engine = engine_override or engine

    def get_with_ingredients(
        self,
        session: Session,
        recipe_id: int,
    ):
        return self.data_accessor.get_with_ingredients(session, recipe_id)

    def has_expansion(
        self,
        session: Session,
        expansion_id: int,
    ):
        return self.data_accessor.has_expansion(session, expansion_id)

    def get_recipe(self, recipe_id: int):
        with Session(self.engine) as session:
            recipe = self.get_with_ingredients(session, recipe_id)

            if recipe is None:
                raise HTTPException(status_code=404, detail="Recipe not found")

            return recipe

    def get_recipes(
        self,
        expansion_id: int | None = None,
        profession_id: int | None = None,
    ):
        from .expansions import ExpansionService

        expansion_service = ExpansionService()

        with Session(self.engine) as session:
            if expansion_id is not None:
                expansion = expansion_service.get(session, expansion_id)

                if expansion is None:
                    raise HTTPException(status_code=404, detail="Expansion not found")

            if profession_id is not None:
                profession = self.profession_service.get(session, profession_id)

                if profession is None:
                    raise HTTPException(status_code=404, detail="Profession not found")

            return self.data_accessor.get_filtered(
                session,
                expansion_id,
                profession_id,
            )

    def create_recipe(self, recipe_data: RecipeCreate):
        from .expansions import ExpansionService

        expansion_service = ExpansionService()

        with Session(self.engine) as session:
            name = clean_name(recipe_data.name)
            profession = self.profession_service.get(session, recipe_data.profession_id)

            if profession is None:
                raise HTTPException(status_code=404, detail="Profession not found")

            expansion = expansion_service.get(session, recipe_data.expansion_id)

            if expansion is None:
                raise HTTPException(status_code=404, detail="Expansion not found")

            resolved = self.recipe_ingredient_service.resolve_ingredients(recipe_data.ingredients, session=session)

            recipe = Recipe(
                name=name,
                profession_id=recipe_data.profession_id,
                expansion_id=recipe_data.expansion_id,
                profit_per_craft=recipe_data.profit_per_craft,
            )
            recipe = self.create(entity=recipe, session=session)

            self.recipe_ingredient_service.add_ingredient_links(
                recipe.id,
                resolved,
                session=session,
            )

            session.commit()

            recipe = self.get_with_ingredients(session, recipe.id)

            return recipe

    def update_recipe(
        self,
        recipe_id: int,
        recipe_data: RecipeUpdate,
    ):
        from .expansions import ExpansionService

        expansion_service = ExpansionService()

        with Session(self.engine) as session:
            recipe = self.get(session, recipe_id)

            if recipe is None:
                raise HTTPException(status_code=404, detail="Recipe not found")

            changes = recipe_data.model_dump(exclude_unset=True, exclude={"ingredients"})

            if "name" in changes:
                changes["name"] = clean_name(changes["name"])

            if "profession_id" in changes:
                profession = self.profession_service.get(session, changes["profession_id"])

                if profession is None:
                    raise HTTPException(status_code=404, detail="Profession not found")

            if "expansion_id" in changes:
                expansion = expansion_service.get(session, changes["expansion_id"])

                if expansion is None:
                    raise HTTPException(status_code=404, detail="Expansion not found")

            resolved = None

            if "ingredients" in recipe_data.model_fields_set:
                resolved = self.recipe_ingredient_service.resolve_ingredients(recipe_data.ingredients, session=session)

            for field, value in changes.items():
                setattr(
                    recipe,
                    field,
                    value,
                )

            recipe = self.update(entity=recipe, session=session)

            if resolved is not None:
                self.recipe_ingredient_service.delete_for_recipe(session, recipe_id)
                self.recipe_ingredient_service.add_ingredient_links(
                    recipe_id,
                    resolved,
                    session=session,
                )

            session.commit()

            recipe = self.get_with_ingredients(session, recipe_id)

            return recipe

    def delete_recipe(self, recipe_id: int):
        with Session(self.engine) as session:
            recipe = self.get(session, recipe_id)

            if recipe is None:
                raise HTTPException(status_code=404, detail="Recipe not found")

            self.delete(session, recipe)

            session.commit()

    def calculate_recipe(
        self,
        recipe_id: int,
        crafts: int,
    ):
        with Session(self.engine) as session:
            if crafts < 0:
                raise HTTPException(status_code=400, detail="Craft count cannot be negative")

            recipe = self.get_with_ingredients(session, recipe_id)

            if recipe is None:
                raise HTTPException(status_code=404, detail="Recipe not found")

            ingredient_totals = {}

            for link in recipe.ingredients:
                name = link.ingredient.name
                amount = link.amount_required * crafts
                ingredient_totals[name] = ingredient_totals.get(name, 0) + amount

            return ingredient_totals

    def update_recipe_profit(
        self,
        recipe_id: int,
        profit_data: RecipeProfitUpdate,
    ):
        with Session(self.engine) as session:
            recipe = self.get(session, recipe_id)

            if recipe is None:
                raise HTTPException(status_code=404, detail="Recipe not found")

            recipe.profit_per_craft = profit_data.profit_per_craft
            recipe = self.update(entity=recipe, session=session)

            session.commit()

            recipe = self.get_with_ingredients(session, recipe_id)

            return recipe