from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..models import Ingredient
from ..dtos import IngredientCreate
from ..database import get_session

router = APIRouter(
    prefix="/ingredients",
    tags=["ingredients"]
)

@router.post("/", response_model=Ingredient)
def create_ingredient(ingredient_data: IngredientCreate, session: Session = Depends(get_session)):
    name = ingredient_data.name.strip()
    if not name:
        raise HTTPException(
            status_code=400,
            detail="Ingredient name cannot be blank",
        )

    ingredient = Ingredient(name=name)
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    return ingredient

@router.get("/", response_model=list[Ingredient])
def get_ingredients(session: Session = Depends(get_session)):
    statement = select(Ingredient)
    results = session.exec(statement).all()
    return results