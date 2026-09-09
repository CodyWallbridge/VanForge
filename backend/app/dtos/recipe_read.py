from pydantic import BaseModel, ConfigDict
from typing import List
from .recipe_ingredient_read import RecipeIngredientRead

class RecipeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    profit_per_craft: int = 0
    profession_id: int
    expansion_id: int
    ingredients: List[RecipeIngredientRead] = []
