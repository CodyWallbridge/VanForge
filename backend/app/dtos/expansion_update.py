from pydantic import BaseModel, Field

class ExpansionUpdate(BaseModel):
    name: str = Field(min_length=1)
