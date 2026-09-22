from sqlmodel import Session, select
from ..models import Character
from .base import CRUDBase

class CharacterCRUD(CRUDBase[Character]):
    def get_for_account(
        self,
        session: Session,
        character_id: int,
        account_id: int,
    ):
        return session.exec(
            select(Character).where(
                Character.id == character_id,
                Character.account_id == account_id,
            ),
        ).first()

    def get_all_for_account(
        self,
        session: Session,
        account_id: int,
    ):
        return session.exec(
            select(Character)
            .where(Character.account_id == account_id)
            .order_by(Character.id),
        ).all()

characters = CharacterCRUD(Character)