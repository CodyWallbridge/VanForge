from sqlmodel import SQLModel
from .ingredient_read import IngredientRead

class RecipeIngredientRead(SQLModel):
    amount_required: int
    ingredient: IngredientRead
