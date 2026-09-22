from fastapi import HTTPException
from sqlmodel import Session
from .settings import SettingsService
from .recipes import RecipeService
from ..backend_models.character_recipe import character_recipes
from ..backend_models.character import characters
from ..models import Character, CharacterRecipe
from ..dtos import CharacterCreate, CharacterUpdate
from ..dtos import CharacterRecipeCreate, CharacterRecipeUpdate
from .common import validate_professions
from ..utils.validation import clean_name
from .base import BaseService
from ..database import engine

class CharacterService(BaseService):
    model_class = Character
    data_accessor = characters
    settings_service = SettingsService()
    recipe_service = RecipeService()

    def __init__(self, engine_override=None):
        self.engine = engine_override or engine

    def get_for_account(
        self,
        session: Session,
        character_id: int,
        account_id: int,
    ):
        return self.data_accessor.get_for_account(
            session,
            character_id,
            account_id,
        )

    def get_character(
        self,
        character_id: int,
        account_id: int,
    ):
        with Session(self.engine) as session:
            character = self.get_for_account(
                session,
                character_id,
                account_id,
            )

            if character is None:
                raise HTTPException(status_code=404, detail="Character not found")

            return character

    def get_characters(self, account_id: int):
        with Session(self.engine) as session:
            return self.data_accessor.get_all_for_account(session, account_id)

    def delete_character(
        self,
        character_id: int,
        account_id: int,
    ):
        with Session(self.engine) as session:
            character = self.get_for_account(
                session,
                character_id,
                account_id,
            )

            if character is None:
                raise HTTPException(status_code=404, detail="Character not found")

            self.delete(session, character)

            session.commit()

    def create_character(
        self,
        character_data: CharacterCreate,
        account_id: int,
    ):
        with Session(self.engine) as session:
            name = clean_name(character_data.name)

            validate_professions(
                session,
                character_data.profession1_id,
                character_data.profession2_id,
            )

            character = Character(
                account_id=account_id,
                name=name,
                profession1_id=character_data.profession1_id,
                profession2_id=character_data.profession2_id,
                concentration=character_data.concentration,
            )

            character = self.create(entity=character, session=session)

            session.commit()
            session.refresh(character)

            return character

    def update_character(
        self,
        character_id: int,
        character_data: CharacterUpdate,
        account_id: int,
    ):
        with Session(self.engine) as session:
            character = self.get_for_account(
                session,
                character_id,
                account_id,
            )

            if character is None:
                raise HTTPException(status_code=404, detail="Character not found")

            changes = character_data.model_dump(exclude_unset=True)

            if "name" in changes:
                changes["name"] = clean_name(changes["name"])

            first_profession_id = changes.get("profession1_id", character.profession1_id)
            second_profession_id = changes.get("profession2_id", character.profession2_id)
            validate_professions(
                session,
                first_profession_id,
                second_profession_id,
            )

            for field, value in changes.items():
                setattr(
                    character,
                    field,
                    value,
                )

            character = self.update(entity=character, session=session)

            session.commit()
            session.refresh(character)

            return character

    def get_character_recipes(
        self,
        character_id: int,
        account_id: int,
    ):
        with Session(self.engine) as session:
            character = self.get_for_account(
                session,
                character_id,
                account_id,
            )

            if character is None:
                raise HTTPException(status_code=404, detail="Character not found")

            app_settings = self.settings_service.get_current(session, account_id)

            if app_settings is None:
                raise HTTPException(status_code=400, detail="Select an expansion before viewing current recipes")

            assignments = character_recipes.get_current(
                session,
                character,
                app_settings.current_expansion_id,
            )

            return assignments

    def assign_recipe(
        self,
        character_id: int,
        recipe_data: CharacterRecipeCreate,
        account_id: int,
    ):
        with Session(self.engine) as session:
            character = self.get_for_account(
                session,
                character_id,
                account_id,
            )

            if character is None:
                raise HTTPException(status_code=404, detail="Character not found")

            recipe = self.recipe_service.get(session, recipe_data.recipe_id)

            if recipe is None:
                raise HTTPException(status_code=404, detail="Recipe not found")

            if recipe.profession_id not in (character.profession1_id, character.profession2_id):
                raise HTTPException(status_code=400, detail="Recipe does not belong to either active profession")

            existing = character_recipes.get_by_character_recipe(
                session,
                character_id,
                recipe.id,
            )

            if existing is not None:
                raise HTTPException(status_code=409, detail="Character already knows this recipe")

            assignment = CharacterRecipe(
                character_id=character_id,
                recipe_id=recipe.id,
                concentration_cost=recipe_data.concentration_cost,
            )
            assignment = character_recipes.create(session, assignment)

            session.commit()
            session.refresh(assignment)

            return assignment
        
    def update_character_recipe(
        self,
        character_id: int,
        recipe_id: int,
        recipe_data: CharacterRecipeUpdate,
        account_id: int,
    ):
        with Session(self.engine) as session:
            character = self.get_for_account(
                session,
                character_id,
                account_id,
            )

            if character is None:
                raise HTTPException(status_code=404, detail="Character not found")

            assignment = character_recipes.get_by_character_recipe(
                session,
                character_id,
                recipe_id,
            )

            if assignment is None:
                raise HTTPException(status_code=404, detail="Character recipe not found")

            assignment.concentration_cost = recipe_data.concentration_cost
            assignment = character_recipes.update(session, assignment)

            session.commit()
            session.refresh(assignment)

            return assignment

    def remove_character_recipe(
        self,
        character_id: int,
        recipe_id: int,
        account_id: int,
    ):
        with Session(self.engine) as session:
            character = self.get_for_account(
                session,
                character_id,
                account_id,
            )

            if character is None:
                raise HTTPException(status_code=404, detail="Character not found")

            assignment = character_recipes.get_by_character_recipe(
                session,
                character_id,
                recipe_id,
            )

            if assignment is None:
                raise HTTPException(status_code=404, detail="Character recipe not found")

            character_recipes.delete(session, assignment.id)

            session.commit()
