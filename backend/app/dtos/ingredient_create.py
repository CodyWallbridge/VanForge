from sqlmodel import SQLModel, Field

class IngredientCreate(SQLModel):
    name: str = Field(min_length=1)