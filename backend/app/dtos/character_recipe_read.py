from pydantic import BaseModel, ConfigDict

class CharacterRecipeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    character_id: int
    recipe_id: int
    concentration_cost: int
