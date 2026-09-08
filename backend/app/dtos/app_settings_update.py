from sqlmodel import SQLModel

class AppSettingsUpdate(SQLModel):
    current_expansion_id: int
