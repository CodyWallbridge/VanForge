from pydantic import BaseModel, Field

class CharacterRecipeUpdate(BaseModel):
    concentration_cost: int = Field(gt=0)
