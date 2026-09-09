from pydantic import BaseModel

class RecipeProfitUpdate(BaseModel):
    profit_per_craft: int