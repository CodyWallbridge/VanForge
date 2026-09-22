from fastapi import APIRouter, Depends
from ..dependencies import get_current_account
from ..services.settings import SettingsService
from ..dtos import AppSettingsRead, AppSettingsUpdate
from ..models import Account

settings_service = SettingsService()

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get('/', response_model=AppSettingsRead)
def get_settings(account: Account = Depends(get_current_account)):
    return settings_service.get_settings(account.id)

@router.patch('/', response_model=AppSettingsRead)
def update_settings(settings_data: AppSettingsUpdate, account: Account = Depends(get_current_account)):
    return settings_service.update_settings(settings_data, account.id)
