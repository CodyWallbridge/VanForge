from fastapi import APIRouter
from ..services.professions import ProfessionService
from ..dtos import ProfessionRead

profession_service = ProfessionService()

router = APIRouter(prefix="/professions", tags=["professions"])

@router.get('/', response_model=list[ProfessionRead])
def get_professions():
    return profession_service.get_professions()
