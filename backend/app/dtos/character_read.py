from pydantic import BaseModel, ConfigDict

class CharacterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    profession1_id: int
    profession2_id: int
    concentration: int
