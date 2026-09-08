from sqlmodel import SQLModel, Field

class CharacterRecipeUpdate(SQLModel):
    concentration_cost: int = Field(gt=0)
