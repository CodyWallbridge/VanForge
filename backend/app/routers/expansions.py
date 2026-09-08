from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select
from ..database import get_session
from ..models import AppSettings, Expansion, Recipe
from ..dtos import ExpansionCreate, ExpansionRead, ExpansionUpdate
from ..services.common import clean_name, commit_changes, find_named, require_record

router = APIRouter(prefix="/expansions", tags=["expansions"])

@router.get("/", response_model=list[ExpansionRead])
def get_expansions(session: Session = Depends(get_session)):
    return session.exec(
        select(Expansion).order_by(Expansion.id)
    ).all()

@router.get("/{expansion_id}", response_model=ExpansionRead)
def get_expansion(expansion_id: int, session: Session = Depends(get_session)):
    return require_record(session, Expansion, expansion_id)

@router.post("/", response_model=ExpansionRead, status_code=201)
def create_expansion(expansion_data: ExpansionCreate, session: Session = Depends(get_session)):
    name = clean_name(expansion_data.name)

    if find_named(session, Expansion, name) is not None:
        raise HTTPException(status_code=409, detail="Expansion name already exists")

    expansion = Expansion(name=name)
    session.add(expansion)

    commit_changes(session)
    session.refresh(expansion)

    return expansion

@router.patch("/{expansion_id}", response_model=ExpansionRead)
def update_expansion(expansion_id: int, expansion_data: ExpansionUpdate, session: Session = Depends(get_session)):
    expansion = require_record(session, Expansion, expansion_id)
    name = clean_name(expansion_data.name)
    existing = find_named(session, Expansion, name)

    if existing is not None and existing.id != expansion_id:
        raise HTTPException(status_code=409, detail="Expansion name already exists")

    expansion.name = name
    session.add(expansion)

    commit_changes(session)
    session.refresh(expansion)

    return expansion

@router.delete("/{expansion_id}", status_code=204)
def delete_expansion(expansion_id: int, session: Session = Depends(get_session)):
    expansion = require_record(session, Expansion, expansion_id)
    selected = session.exec(
        select(AppSettings).where(AppSettings.current_expansion_id == expansion_id)
    ).first()

    if selected is not None:
        raise HTTPException(status_code=409, detail="Cannot delete the selected expansion")

    recipe = session.exec(
        select(Recipe.id).where(Recipe.expansion_id == expansion_id)
    ).first()

    if recipe is not None:
        raise HTTPException(status_code=409, detail="Cannot delete an expansion containing recipes")

    session.delete(expansion)

    commit_changes(session)

    return Response(status_code=204)
