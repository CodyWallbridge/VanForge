from pydantic import BaseModel, Field

class IngredientCreate(BaseModel):
    name: str = Field(min_length=1)