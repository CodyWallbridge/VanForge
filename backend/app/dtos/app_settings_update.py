from pydantic import BaseModel

class AppSettingsUpdate(BaseModel):
    current_expansion_id: int
