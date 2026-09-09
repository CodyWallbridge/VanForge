from pydantic import BaseModel, ConfigDict
from .expansion_read import ExpansionRead

class AppSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    current_expansion_id: int
    current_expansion: ExpansionRead
