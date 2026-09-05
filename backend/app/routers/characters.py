from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..models import Character, CharacterRecipe, Profession, Recipe
from ..dtos import CharacterRecipeCreate, CharacterCreate
from ..database import get_session

router = APIRouter(
    prefix="/characters",
    tags=["characters"]
)

@router.post("/", response_model=Character)
def create_character(character_data: CharacterCreate, session: Session = Depends(get_session)):
    name = character_data.name.strip()
    if not name:
        raise HTTPException(
            status_code=400,
            detail="Character name cannot be blank",
        )

    if character_data.profession1_id == character_data.profession2_id:
        raise HTTPException(
            status_code=400,
            detail="Character professions must be different",
        )

    for profession_id in (character_data.profession1_id, character_data.profession2_id):
        if session.get(Profession, profession_id) is None:
            raise HTTPException(
                status_code=400,
                detail=f"Profession {profession_id} does not exist",
            )

    character = Character(
        name=name,
        profession1_id=character_data.profession1_id,
        profession2_id=character_data.profession2_id,
        concentration=character_data.concentration,
    )
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