from sqlmodel import SQLModel

class CharacterPlanItem(SQLModel):
    character_id: int
    recipe_id: int
    crafts: int
