from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from ..models import Recipe, RecipeIngredient
from ..dtos import RecipeCreate, RecipeRead
from ..database import get_session

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"]
)

@router.post("/")
def create_recipe(recipe_data: RecipeCreate, session: Session = Depends(get_session)):
    recipe = Recipe(
        name=recipe_data.name,
        profession_id=recipe_data.profession_id,
        profit_per_craft=recipe_data.profit_per_craft,
    )

    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    for ing in recipe_data.ingredients:
        ri = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ing.ingredient_id,
            amount_required=ing.amount_required
        )
        session.add(ri)

    session.commit()

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

    result = {}

    for ri in recipe.ingredients:
        name = ri.ingredient.name
        total = ri.amount_required * crafts

        result[name] = total

    return result