from fastapi import APIRouter
from ..services.settings import SettingsService
from ..dtos import AppSettingsRead, AppSettingsUpdate

settings_service = SettingsService()

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get('/', response_model=AppSettingsRead)
def get_settings():
    return settings_service.get_settings()

@router.patch('/', response_model=AppSettingsRead)
def update_settings(settings_data: AppSettingsUpdate):
    return settings_service.update_settings(settings_data)
