from fastapi import HTTPException
from sqlmodel import Session
from ..backend_models.profession import professions

def validate_professions(
    session: Session,
    first: int,
    second: int,
):
    if first == second:
        raise HTTPException(status_code=400, detail="Character professions must be different")

    for profession_id in (first, second):
        profession = professions.get(session, profession_id)

        if profession is None:
            raise HTTPException(status_code=404, detail="Profession not found")
