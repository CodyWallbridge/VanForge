from sqlmodel import SQLModel
from .expansion_read import ExpansionRead

class AppSettingsRead(SQLModel):
    id: int
    current_expansion_id: int
    current_expansion: ExpansionRead
