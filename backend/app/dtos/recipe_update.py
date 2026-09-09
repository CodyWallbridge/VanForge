from pydantic import Field
from .update_request import UpdateRequest
from .recipe_ingredient_create import RecipeIngredientCreate

class RecipeUpdate(UpdateRequest):
    name: str | None = Field(default=None, min_length=1)
    profit_per_craft: int | None = None
    profession_id: int | None = None
    expansion_id: int | None = None
    ingredients: list[RecipeIngredientCreate] | None = None
