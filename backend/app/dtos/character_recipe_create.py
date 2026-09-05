from sqlmodel import SQLModel, Field

class CharacterRecipeCreate(SQLModel):
    recipe_id: int
    concentration_cost: int = Field(gt=0)