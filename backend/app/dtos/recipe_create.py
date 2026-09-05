from sqlmodel import SQLModel
from typing import List
from .recipe_ingredient_create import RecipeIngredientCreate

class RecipeCreate(SQLModel):
    name: str
    profit_per_craft: int = 0
    profession_id: int
    ingredients: List[RecipeIngredientCreate]
