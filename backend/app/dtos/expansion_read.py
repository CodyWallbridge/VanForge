from sqlmodel import SQLModel

class ExpansionRead(SQLModel):
    id: int
    name: str
