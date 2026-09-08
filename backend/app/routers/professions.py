from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..database import get_session
from ..models import Profession
from ..dtos import ProfessionRead

router = APIRouter(prefix="/professions", tags=["professions"])

@router.get("/", response_model=list[ProfessionRead])
def get_professions(session: Session = Depends(get_session)):
    return session.exec(
        select(Profession).order_by(Profession.name)
    ).all()
