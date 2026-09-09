from pydantic import BaseModel
from .character_plan_item import CharacterPlanItem
from .character_optimization_read import CharacterOptimizationRead

class OptimizationRead(BaseModel):
    expansion_id: int
    total_profit: int
    crafts: list[CharacterPlanItem]
    characters: list[CharacterOptimizationRead]
