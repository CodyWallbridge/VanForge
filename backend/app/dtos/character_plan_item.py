from sqlmodel import SQLModel, Field

class CharacterPlanItem(SQLModel):
    character_id: int
    recipe_id: int
    crafts: int = Field(ge=0)