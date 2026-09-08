from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..database import get_session
from ..models import AppSettings, Expansion
from ..dtos import AppSettingsRead, AppSettingsUpdate
from ..services.common import commit_changes, current_settings, require_record

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/", response_model=AppSettingsRead)
def get_settings(session: Session = Depends(get_session)):
    return current_settings(session)

@router.patch("/", response_model=AppSettingsRead)
def update_settings(settings_data: AppSettingsUpdate, session: Session = Depends(get_session)):
    expansion = require_record(session, Expansion, settings_data.current_expansion_id)
    settings = session.get(AppSettings, 1)

    if settings is None:
        settings = AppSettings(id=1, current_expansion_id=expansion.id)
    else:
        settings.current_expansion_id = expansion.id

    session.add(settings)

    commit_changes(session)
    session.refresh(settings)

    return settings
