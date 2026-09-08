from sqlmodel import SQLModel

class CharacterRead(SQLModel):
    id: int
    name: str
    profession1_id: int
    profession2_id: int
    concentration: int
