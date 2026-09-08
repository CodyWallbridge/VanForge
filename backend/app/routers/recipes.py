from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select, delete
from ..database import get_session
from ..models import Expansion, Profession, Recipe, RecipeIngredient
from ..dtos import RecipeCreate, RecipeRead, RecipeProfitUpdate, RecipeUpdate
from ..services.common import clean_name, commit_changes, require_record
from ..services.recipe_ingredients import add_ingredient_links, resolve_ingredients

router = APIRouter(prefix="/recipes", tags=["recipes"])

def load_recipe(
    session,
    recipe_id,
):
    recipe = session.exec(
        select(Recipe).options(
            selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient)
        ).where(Recipe.id == recipe_id)
    ).first()

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe

@router.post("/", response_model=RecipeRead, status_code=201)
def create_recipe(recipe_data: RecipeCreate, session: Session = Depends(get_session)):
    name = clean_name(recipe_data.name)
    require_record(session, Profession, recipe_data.profession_id)
    require_record(session, Expansion, recipe_data.expansion_id)
    resolved = resolve_ingredients(session, recipe_data.ingredients)

    recipe = Recipe(
        name=name,
        profession_id=recipe_data.profession_id,
        expansion_id=recipe_data.expansion_id,
        profit_per_craft=recipe_data.profit_per_craft,
    )

    try:
        session.add(recipe)
        session.flush()
        add_ingredient_links(session, recipe.id, resolved)

        commit_changes(session)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="Recipe conflicts with existing data") from error

    return load_recipe(session, recipe.id)

@router.get("/", response_model=list[RecipeRead])
def get_recipes(expansion_id: int | None = None, profession_id: int | None = None, session: Session = Depends(get_session)):
    statement = select(Recipe).options(
        selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient)
    )

    if expansion_id is not None:
        require_record(session, Expansion, expansion_id)

        statement = statement.where(Recipe.expansion_id == expansion_id)

    if profession_id is not None:
        require_record(session, Profession, profession_id)

        statement = statement.where(Recipe.profession_id == profession_id)

    return session.exec(
        statement.order_by(Recipe.id)
    ).all()

@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(recipe_id: int, session: Session = Depends(get_session)):
    return load_recipe(session, recipe_id)

@router.patch("/{recipe_id}", response_model=RecipeRead)
def update_recipe(recipe_id: int, recipe_data: RecipeUpdate, session: Session = Depends(get_session)):
    recipe = require_record(session, Recipe, recipe_id)

    changes = recipe_data.model_dump(exclude_unset=True, exclude={"ingredients"})

    if "name" in changes:
        changes["name"] = clean_name(changes["name"])

    if "profession_id" in changes:
        require_record(session, Profession, changes["profession_id"])

    if "expansion_id" in changes:
        require_record(session, Expansion, changes["expansion_id"])

    resolved = None

    if "ingredients" in recipe_data.model_fields_set:
        resolved = resolve_ingredients(session, recipe_data.ingredients)

    try:
        for field, value in changes.items():
            setattr(recipe, field, value)

        session.add(recipe)

        if resolved is not None:
            session.exec(
                delete(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id)
            )
            add_ingredient_links(session, recipe_id, resolved)

        commit_changes(session)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="Recipe conflicts with existing data") from error

    return load_recipe(session, recipe_id)

@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int, session: Session = Depends(get_session)):
    recipe = require_record(session, Recipe, recipe_id)

    session.delete(recipe)

    commit_changes(session)

    return Response(status_code=204)

@router.post("/{recipe_id}/calculate")
def calculate_recipe(recipe_id: int, crafts: int, session: Session = Depends(get_session)):
    recipe = load_recipe(session, recipe_id)

    if crafts < 0:
        raise HTTPException(status_code=400, detail="Craft count cannot be negative")

    result = {}

    for link in recipe.ingredients:
        name = link.ingredient.name
        result[name] = result.get(name, 0) + link.amount_required * crafts

    return result

@router.patch("/{recipe_id}/profit", response_model=RecipeRead)
def update_recipe_profit(recipe_id: int, profit_data: RecipeProfitUpdate, session: Session = Depends(get_session)):
    recipe = require_record(session, Recipe, recipe_id)

    recipe.profit_per_craft = profit_data.profit_per_craft
    session.add(recipe)

    commit_changes(session)

    return load_recipe(session, recipe_id)
