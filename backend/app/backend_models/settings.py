from sqlmodel import Session, select
from ..models import AppSettings
from .base import CRUDBase

class SettingsCRUD(CRUDBase[AppSettings]):
    def get_current(
        self,
        session: Session,
        account_id: int,
    ):
        return session.exec(
            select(AppSettings).where(AppSettings.account_id == account_id),
        ).first()

    def uses_expansion(self, session: Session, expansion_id):
        settings = session.exec(
            select(AppSettings)
            .where(AppSettings.current_expansion_id == expansion_id),
        ).first()

        return settings is not None

settings = SettingsCRUD(AppSettings)