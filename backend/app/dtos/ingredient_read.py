from sqlmodel import SQLModel

class IngredientRead(SQLModel):
    id: int
    name: str
