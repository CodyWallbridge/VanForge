from pydantic import BaseModel
from .profession_optimization_read import ProfessionOptimizationRead

class CharacterOptimizationRead(BaseModel):
    character_id: int
    character_name: str
    profit: int
    professions: list[ProfessionOptimizationRead]
