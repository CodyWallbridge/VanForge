from sqlmodel import SQLModel, Field

class RecipeIngredientCreate(SQLModel):
    ingredient_id: int
    amount_required:int = Field(gt=0)
