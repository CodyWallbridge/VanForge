from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select
from ..database import get_session
from ..models import Character, CharacterRecipe, Recipe
from ..dtos import CharacterCreate, CharacterRead, CharacterUpdate
from ..dtos import CharacterRecipeCreate, CharacterRecipeRead, CharacterRecipeUpdate
from ..services.common import clean_name, commit_changes, current_settings, require_record, validate_professions

router = APIRouter(prefix="/characters", tags=["characters"])

@router.post("/", response_model=CharacterRead, status_code=201)
def create_character(character_data: CharacterCreate, session: Session = Depends(get_session)):
    name = clean_name(character_data.name)
    validate_professions(session, character_data.profession1_id, character_data.profession2_id)

    character = Character(
        name=name,
        profession1_id=character_data.profession1_id,
        profession2_id=character_data.profession2_id,
        concentration=character_data.concentration,
    )
    session.add(character)

    commit_changes(session)
    session.refresh(character)

    return character

@router.get("/", response_model=list[CharacterRead])
def get_characters(session: Session = Depends(get_session)):
    return session.exec(
        select(Character).order_by(Character.id)
    ).all()

@router.get("/{character_id}", response_model=CharacterRead)
def get_character(character_id: int, session: Session = Depends(get_session)):
    return require_record(session, Character, character_id)

@router.patch("/{character_id}", response_model=CharacterRead)
def update_character(character_id: int, character_data: CharacterUpdate, session: Session = Depends(get_session)):
    character = require_record(session, Character, character_id)

    changes = character_data.model_dump(exclude_unset=True)

    if "name" in changes:
        changes["name"] = clean_name(changes["name"])

    validate_professions(
        session,
        changes.get("profession1_id", character.profession1_id),
        changes.get("profession2_id", character.profession2_id),
    )

    for field, value in changes.items():
        setattr(character, field, value)

    session.add(character)

    commit_changes(session)
    session.refresh(character)

    return character

@router.delete("/{character_id}", status_code=204)
def delete_character(character_id: int, session: Session = Depends(get_session)):
    character = require_record(session, Character, character_id)

    session.delete(character)

    commit_changes(session)

    return Response(status_code=204)

@router.get("/{character_id}/recipes", response_model=list[CharacterRecipeRead])
def get_character_recipes(character_id: int, session: Session = Depends(get_session)):
    character = require_record(session, Character, character_id)
    settings = current_settings(session)

    return session.exec(
        select(CharacterRecipe).join(Recipe).where(
            CharacterRecipe.character_id == character_id,
            Recipe.profession_id.in_([character.profession1_id, character.profession2_id]),
            Recipe.expansion_id == settings.current_expansion_id,
        ).order_by(CharacterRecipe.recipe_id)
    ).all()

@router.post("/{character_id}/recipes", response_model=CharacterRecipeRead, status_code=201)
def assign_recipe(character_id: int, recipe_data: CharacterRecipeCreate, session: Session = Depends(get_session)):
    character = require_record(session, Character, character_id)
    recipe = require_record(session, Recipe, recipe_data.recipe_id)

    if recipe.profession_id not in (character.profession1_id, character.profession2_id):
        raise HTTPException(status_code=400, detail="Recipe does not belong to either active profession")

    existing = session.get(CharacterRecipe, (character_id, recipe.id))

    if existing is not None:
        raise HTTPException(status_code=409, detail="Character already knows this recipe")

    assignment = CharacterRecipe(
        character_id=character_id,
        recipe_id=recipe.id,
        concentration_cost=recipe_data.concentration_cost,
    )
    session.add(assignment)

    commit_changes(session)
    session.refresh(assignment)

    return assignment

@router.patch("/{character_id}/recipes/{recipe_id}", response_model=CharacterRecipeRead)
def update_character_recipe(character_id: int, recipe_id: int, recipe_data: CharacterRecipeUpdate, session: Session = Depends(get_session)):
    require_record(session, Character, character_id)
    assignment = require_record(session, CharacterRecipe, (character_id, recipe_id))

    assignment.concentration_cost = recipe_data.concentration_cost
    session.add(assignment)

    commit_changes(session)
    session.refresh(assignment)

    return assignment

@router.delete("/{character_id}/recipes/{recipe_id}", status_code=204)
def remove_character_recipe(character_id: int, recipe_id: int, session: Session = Depends(get_session)):
    require_record(session, Character, character_id)
    assignment = require_record(session, CharacterRecipe, (character_id, recipe_id))

    session.delete(assignment)

    commit_changes(session)

    return Response(status_code=204)
