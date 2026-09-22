from fastapi import APIRouter, Depends
from ..dependencies import get_current_account
from ..services.professions import ProfessionService
from ..dtos import ProfessionRead

profession_service = ProfessionService()

router = APIRouter(
    prefix="/professions",
    tags=["professions"],
    dependencies=[Depends(get_current_account)],
)

@router.get('/', response_model=list[ProfessionRead])
def get_professions():
    return profession_service.get_professions()
