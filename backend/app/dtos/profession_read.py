from sqlmodel import SQLModel

class ProfessionRead(SQLModel):
    id: int
    name: str
