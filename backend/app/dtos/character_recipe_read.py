from sqlmodel import SQLModel

class CharacterRecipeRead(SQLModel):
    character_id: int
    recipe_id: int
    concentration_cost: int
