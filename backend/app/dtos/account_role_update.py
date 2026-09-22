from typing import Literal
from pydantic import BaseModel

class AccountRoleUpdate(BaseModel):
    role: Literal["user", "admin"]
