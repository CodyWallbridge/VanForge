from pydantic import BaseModel, Field

class CharacterPlanItem(BaseModel):
    character_id: int
    recipe_id: int
    crafts: int = Field(ge=0)