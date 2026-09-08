from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from ..models import AppSettings, Profession

def require_record(
    session,
    model,
    record_id,
):
    record = session.get(model, record_id)

    if record is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")

    return record

def clean_name(
    name,
):
    name = name.strip()

    if not name:
        raise HTTPException(status_code=400, detail="Name cannot be blank")

    return name

def find_named(
    session,
    model,
    name,
):
    # Python casefold handles non-ASCII names consistently with the seed code.
    key = name.strip().casefold()

    records = session.exec(
        select(model).order_by(model.id)
    ).all()

    return next(
        (record for record in records if record.name.strip().casefold() == key),
        None,
    )

def validate_professions(
    session,
    first,
    second,
):
    if first == second:
        raise HTTPException(status_code=400, detail="Character professions must be different")

    for profession_id in (first, second):
        require_record(session, Profession, profession_id)

def current_settings(
    session,
):
    settings = session.get(AppSettings, 1)

    if settings is None:
        raise HTTPException(status_code=400, detail="Select an expansion before planning")

    return settings

def commit_changes(
    session,
):
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="Change conflicts with existing data") from error
