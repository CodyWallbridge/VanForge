from sqlmodel import Session, select
from ..models import Expansion
from .base import CRUDBase

class ExpansionCRUD(CRUDBase[Expansion]):

    def get_by_name(
        self,
        session: Session,
        name: str,
    ):
        key = name.strip().casefold()
        expansions = self.get_all(session)

        for expansion in expansions:
            if expansion.name.strip().casefold() == key:
                return expansion

        return None

expansions = ExpansionCRUD(Expansion)