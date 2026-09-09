from pydantic import BaseModel, Field

class ExpansionCreate(BaseModel):
    name: str = Field(min_length=1)
