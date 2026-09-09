from pydantic import BaseModel, Field

class CharacterCreate(BaseModel):
    name: str = Field(min_length=1)
    profession1_id: int
    profession2_id: int
    concentration: int = Field(
        default=1000,
        ge=0,
        le=1000,
    )