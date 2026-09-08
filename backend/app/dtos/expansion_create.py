from sqlmodel import SQLModel, Field

class ExpansionCreate(SQLModel):
    name: str = Field(min_length=1)
