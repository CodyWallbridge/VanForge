from fastapi import HTTPException
from sqlmodel import Session
from ..database import engine
from ..backend_models.settings import settings
from ..models import AppSettings
from ..dtos import AppSettingsRead, AppSettingsUpdate, ExpansionRead
from .base import BaseService

class SettingsService(BaseService):
    model_class = AppSettings
    data_accessor = settings

    def __init__(self, engine_override=None):
        self.engine = engine_override or engine

    def get_current(self, session: Session):
        return self.data_accessor.get_current(session)

    def uses_expansion(
        self,
        session: Session,
        expansion_id: int,
    ):
        return self.data_accessor.uses_expansion(session, expansion_id)

    def get_settings(self):
        with Session(self.engine) as session:
            current = self.get_current(session)

            if current is None:
                raise HTTPException(status_code=400, detail="Select an expansion first")
            
            expansion = current.current_expansion
            expansion_read = ExpansionRead(id=expansion.id, name=expansion.name)
            result = AppSettingsRead(
                id=current.id,
                current_expansion_id=current.current_expansion_id,
                current_expansion=expansion_read,
            )

            return result

    def update_settings(self, settings_data: AppSettingsUpdate):
        from .expansions import ExpansionService

        expansion_service = ExpansionService()

        with Session(self.engine) as session:
            expansion = expansion_service.get(session, settings_data.current_expansion_id)

            if expansion is None:
                raise HTTPException(status_code=404, detail="Expansion not found")

            current = self.get_current(session)

            if current is None:
                current = AppSettings(id=1, current_expansion_id=expansion.id)
                current = self.create(entity=current, session=session)
            else:
                current.current_expansion_id = expansion.id
                current = self.update(entity=current, session=session)

            session.commit()
            session.refresh(current)

            expansion = current.current_expansion
            expansion_read = ExpansionRead(id=expansion.id, name=expansion.name)
            result = AppSettingsRead(
                id=current.id,
                current_expansion_id=current.current_expansion_id,
                current_expansion=expansion_read,
            )

            return result