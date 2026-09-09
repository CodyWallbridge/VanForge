from pydantic import BaseModel, ConfigDict
from .ingredient_read import IngredientRead

class RecipeIngredientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    amount_required: int
    ingredient: IngredientRead
