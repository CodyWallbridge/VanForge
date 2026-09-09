from sqlmodel import Session
from ..database import engine
from ..backend_models.profession import professions
from ..models import Profession
from .base import BaseService

class ProfessionService(BaseService):
    model_class = Profession
    data_accessor = professions

    def __init__(self, engine_override=None):
        self.engine = engine_override or engine

    def get_professions(self):
        with Session(self.engine) as session:
            return self.get_all(session)