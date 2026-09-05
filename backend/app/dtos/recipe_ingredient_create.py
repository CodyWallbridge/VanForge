from sqlmodel import SQLModel

class RecipeIngredientCreate(SQLModel):
    ingredient_id: int
    amount_required: int
