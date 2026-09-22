from fastapi import APIRouter, Depends
from ..dependencies import get_current_account
from ..services.planner import PlannerService
from ..dtos import CharacterPlanItem, OptimizationRequest, OptimizationRead
from ..models import Account

planner_service = PlannerService()

router = APIRouter(prefix="/planner", tags=["planner"])

@router.get('/options/{character_id}')
def get_options(character_id: int, account: Account = Depends(get_current_account)):
    return planner_service.get_options(character_id, account.id)

@router.post('/')
def calculate_plan(plan: list[CharacterPlanItem], account: Account = Depends(get_current_account)):
    return planner_service.calculate_plan(plan, account.id)

@router.post('/optimize', response_model=OptimizationRead)
def optimize_plan(request: OptimizationRequest, account: Account = Depends(get_current_account)):
    return planner_service.optimize_plan(request, account.id)
