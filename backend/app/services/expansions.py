from fastapi import HTTPException
from sqlmodel import Session
from ..database import engine
from ..backend_models.expansion import expansions
from ..models import Expansion
from ..dtos import ExpansionCreate, ExpansionUpdate
from ..utils.validation import clean_name
from .base import BaseService
from .settings import SettingsService
from .recipes import RecipeService

class ExpansionService(BaseService):
    model_class = Expansion
    data_accessor = expansions
    settings_service = SettingsService()
    recipe_service = RecipeService()

    def __init__(self, engine_override=None):
        self.engine = engine_override or engine

    def get_expansion(self, expansion_id: int):
        with Session(self.engine) as session:
            expansion = self.get(session, expansion_id)

            if expansion is None:
                raise HTTPException(status_code=404, detail="Expansion not found")

            return expansion

    def get_expansions(self):
        with Session(self.engine) as session:
            return self.get_all(session)

    def create_expansion(self, expansion_data: ExpansionCreate):
        with Session(self.engine) as session:
            name = clean_name(expansion_data.name)
            existing = self.data_accessor.get_by_name(session, name)

            if existing is not None:
                raise HTTPException(status_code=409, detail="Expansion name already exists")

            expansion = Expansion(name=name)
            expansion = self.create(entity=expansion, session=session)

            session.commit()
            session.refresh(expansion)

            return expansion

    def update_expansion(
        self,
        expansion_id: int,
        expansion_data: ExpansionUpdate,
    ):
        with Session(self.engine) as session:
            expansion = self.get(session, expansion_id)

            if expansion is None:
                raise HTTPException(status_code=404, detail="Expansion not found")

            name = clean_name(expansion_data.name)
            existing = self.data_accessor.get_by_name(session, name)

            if existing is not None and existing.id != expansion_id:
                raise HTTPException(status_code=409, detail="Expansion name already exists")

            expansion.name = name
            expansion = self.update(entity=expansion, session=session)

            session.commit()
            session.refresh(expansion)

            return expansion

    def delete_expansion(self, expansion_id: int):
        with Session(self.engine) as session:
            expansion = self.get(session, expansion_id)

            if expansion is None:
                raise HTTPException(status_code=404, detail="Expansion not found")

            selected = self.settings_service.uses_expansion(session, expansion_id)

            if selected:
                raise HTTPException(status_code=409, detail="Cannot delete the selected expansion")

            has_recipes = self.recipe_service.has_expansion(session, expansion_id)

            if has_recipes:
                raise HTTPException(status_code=409, detail="Cannot delete an expansion containing recipes")

            self.delete(session, expansion)

            session.commit()
