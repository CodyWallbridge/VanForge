from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..database import get_session
from ..models import Ingredient
from ..dtos import IngredientCreate, IngredientRead
from ..services.common import clean_name, commit_changes, find_named

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

@router.post("/", response_model=IngredientRead)
def create_ingredient(ingredient_data: IngredientCreate, session: Session = Depends(get_session)):
    name = clean_name(ingredient_data.name)
    ingredient = find_named(session, Ingredient, name)

    if ingredient is None:
        ingredient = Ingredient(name=name)
        session.add(ingredient)

        commit_changes(session)
        session.refresh(ingredient)

    return ingredient

@router.get("/", response_model=list[IngredientRead])
def get_ingredients(search: str | None = None, session: Session = Depends(get_session)):
    ingredients = session.exec(
        select(Ingredient).order_by(Ingredient.name, Ingredient.id)
    ).all()

    if search is not None:
        key = search.strip().casefold()
        ingredients = [ingredient for ingredient in ingredients if key in ingredient.name.casefold()]

    return ingredients
