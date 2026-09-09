from pydantic import BaseModel

class ProfessionOptimizationRead(BaseModel):
    profession_id: int
    profit: int
    concentration_used: int
    concentration_remaining: int
