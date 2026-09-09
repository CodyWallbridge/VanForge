from pydantic import BaseModel, ConfigDict

class IngredientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
