from sqlmodel import Session, select
from ..models import Profession
from .base import CRUDBase

class ProfessionCRUD(CRUDBase[Profession]):
    def get_all(self, session: Session):
        return session.exec(
            select(Profession)
            .order_by(Profession.name),
        ).all()

professions = ProfessionCRUD(Profession)