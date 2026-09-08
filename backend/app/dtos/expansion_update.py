from sqlmodel import SQLModel, Field

class ExpansionUpdate(SQLModel):
    name: str = Field(min_length=1)
