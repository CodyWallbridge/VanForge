from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..models import Ingredient
from ..database import get_session

router = APIRouter(
    prefix="/ingredients",
    tags=["ingredients"]
)

@router.post("/", response_model=Ingredient)
def create_ingredient(
    ingredient: Ingredient,
    session: Session = Depends(get_session)
):
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    return ingredient

@router.get("/", response_model=list[Ingredient])
def get_ingredients(session: Session = Depends(get_session)):
    statement = select(Ingredient)
    results = session.exec(statement).all()
    return results