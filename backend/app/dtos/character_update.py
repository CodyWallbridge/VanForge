from pydantic import Field
from .update_request import UpdateRequest

class CharacterUpdate(UpdateRequest):
    name: str | None = Field(default=None, min_length=1)
    profession1_id: int | None = None
    profession2_id: int | None = None
    concentration: int | None = Field(
        default=None,
        ge=0,
        le=1000,
    )
