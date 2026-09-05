from sqlmodel import SQLModel
from typing import List
from .recipe_ingredient_read import RecipeIngredientRead

class RecipeRead(SQLModel):
    id: int
    name: str
    profit_per_craft: int = 0
    profession_id: int
    expansion_id: int
    ingredients: List[RecipeIngredientRead] = []
