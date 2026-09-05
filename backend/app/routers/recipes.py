from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from ..models import Expansion, Ingredient, Profession, Recipe, RecipeIngredient
from ..dtos import RecipeCreate, RecipeRead, RecipeProfitUpdate
from ..database import get_session

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"]
)

@router.post("/")
def create_recipe(recipe_data: RecipeCreate, session: Session = Depends(get_session)):
    name = recipe_data.name.strip()
    if not name:
        raise HTTPException(
            status_code=400,
            detail="Recipe name cannot be blank",
        )
    
    if session.get(Profession, recipe_data.profession_id) is None:
        raise HTTPException(
            status_code=400,
            detail="Profession does not exist",
        )

    if session.get(Expansion, recipe_data.expansion_id) is None:
        raise HTTPException(
            status_code=400,
            detail="Expansion does not exist",
        )

    ingredient_ids = set()

    for ingredient in recipe_data.ingredients:
        if ingredient.ingredient_id in ingredient_ids:
            raise HTTPException(
                status_code=400,
                detail="Each ingredient can only appear once in a recipe",
            )

        if session.get(Ingredient, ingredient.ingredient_id) is None:
            raise HTTPException(
                status_code=400,
                detail=f"Ingredient {ingredient.ingredient_id} does not exist",
            )

        ingredient_ids.add(ingredient.ingredient_id)
        
    recipe = Recipe(
        name=name,
        profession_id=recipe_data.profession_id,
        expansion_id=recipe_data.expansion_id,
        profit_per_craft=recipe_data.profit_per_craft,
    )

    session.add(recipe)
    session.flush()

    for ing in recipe_data.ingredients:
        ri = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ing.ingredient_id,
            amount_required=ing.amount_required
        )
        session.add(ri)

    session.commit()
    session.refresh(recipe)

    return recipe

@router.get("/", response_model=list[RecipeRead])
def get_recipes(session: Session = Depends(get_session)):
    statement = select(Recipe).options(
        selectinload(Recipe.ingredients)
        .selectinload(RecipeIngredient.ingredient)
    )
    results = session.exec(statement).all()
    return results

@router.post("/{recipe_id}/calculate")
def calculate_recipe(recipe_id: int, crafts: int, session: Session = Depends(get_session)):
    statement = select(Recipe).options(
        selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient)
    ).where(Recipe.id == recipe_id)

    recipe = session.exec(statement).first()

    if recipe is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found",
        )

    if crafts < 0:
        raise HTTPException(
            status_code=400,
            detail="Craft count cannot be negative",
        )

    result = {}

    for ri in recipe.ingredients:
        name = ri.ingredient.name
        total = ri.amount_required * crafts

        result[name] = total

    return result

@router.patch(
    "/{recipe_id}/profit",
    response_model=RecipeRead,
)
def update_recipe_profit(recipe_id: int, profit_data: RecipeProfitUpdate, session: Session = Depends(get_session)):
    recipe = session.get(Recipe, recipe_id)

    if recipe is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found",
        )

    recipe.profit_per_craft = profit_data.profit_per_craft
    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    return recipe
