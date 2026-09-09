from sqlmodel import select, Session
from ..models import CharacterRecipe, Recipe
from .base import CRUDBase

class CharacterRecipeCRUD(CRUDBase[CharacterRecipe]):
    def get_by_character_recipe(
        self,
        session: Session,
        character_id: int,
        recipe_id: int,
    ) -> CharacterRecipe | None:
        return session.exec(
            select(CharacterRecipe).where(
                CharacterRecipe.character_id == character_id,
                CharacterRecipe.recipe_id == recipe_id,
            ),
        ).first()

    def get_all(self, session: Session):
        return session.exec(
            select(CharacterRecipe)
            .order_by(CharacterRecipe.character_id, CharacterRecipe.recipe_id),
        ).all()

    def get_current(self, session: Session, character, expansion_id):
        return session.exec(
            select(CharacterRecipe)
            .join(Recipe)
            .where(
                CharacterRecipe.character_id == character.id,
                Recipe.profession_id.in_([character.profession1_id, character.profession2_id]),
                Recipe.expansion_id == expansion_id,
            ).order_by(CharacterRecipe.recipe_id),
        ).all()

character_recipes = CharacterRecipeCRUD(CharacterRecipe)