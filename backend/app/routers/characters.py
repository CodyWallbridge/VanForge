from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..models import Character
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