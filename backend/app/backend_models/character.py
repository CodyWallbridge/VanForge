from ..models import Character
from .base import CRUDBase

class CharacterCRUD(CRUDBase[Character]):
    pass

characters = CharacterCRUD(Character)