from fastapi import APIRouter
from ..services.planner import PlannerService
from ..dtos import CharacterPlanItem, OptimizationRequest, OptimizationRead

planner_service = PlannerService()

router = APIRouter(prefix="/planner", tags=["planner"])

@router.get('/options/{character_id}')
def get_options(character_id: int):
    return planner_service.get_options(character_id)

@router.post('/')
def calculate_plan(plan: list[CharacterPlanItem]):
    return planner_service.calculate_plan(plan)

@router.post('/optimize', response_model=OptimizationRead)
def optimize_plan(request: OptimizationRequest):
    return planner_service.optimize_plan(request)
