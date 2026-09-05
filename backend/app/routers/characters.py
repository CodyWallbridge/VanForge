from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..models import Character, CharacterRecipe, Recipe
from ..dtos import CharacterRecipeCreate
from ..database import get_session

router = APIRouter(
    prefix="/characters",
    tags=["characters"]
)

@router.post("/", response_model=Character)
def create_character(
    character: Character,
    session: Session = Depends(get_session)
):
    session.add(character)
    session.commit()
    session.refresh(character)

    return character

@router.get("/", response_model=list[Character])
def get_characters(session: Session = Depends(get_session)):
    statement = select(Character)
    results = session.exec(statement).all()
    return results

@router.post("/{character_id}/recipes", response_model=CharacterRecipe, status_code=201,)
def assign_recipe(
    character_id: int,
    recipe_data: CharacterRecipeCreate,
    session: Session = Depends(get_session),
):
    character = session.get(Character, character_id)
    if character is None:
        raise HTTPException(
            status_code=404,
            detail="Character not found",
        )

    recipe = session.get(Recipe, recipe_data.recipe_id)
    if recipe is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found",
        )

    if recipe.profession_id not in (character.profession1_id, character.profession2_id):
        raise HTTPException(
            status_code=400,
            detail="Recipe does not belong to either of the character's professions",
        )

    existing = session.get(
        CharacterRecipe,
        (character_id, recipe_data.recipe_id),
    )
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Character already knows this recipe",
        )

    character_recipe = CharacterRecipe(
        character_id=character_id,
        recipe_id=recipe_data.recipe_id,
        concentration_cost=recipe_data.concentration_cost,
    )
    session.add(character_recipe)
    session.commit()
    session.refresh(character_recipe)

    return character_recipe