from pydantic import BaseModel

class AccountRead(BaseModel):
    id: int
    auth_user_id: str
    email: str | None
    role: str