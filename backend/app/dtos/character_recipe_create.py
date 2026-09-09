from pydantic import BaseModel, Field

class CharacterRecipeCreate(BaseModel):
    recipe_id: int
    concentration_cost: int = Field(gt=0)