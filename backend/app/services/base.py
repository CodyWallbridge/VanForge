from abc import ABC
from typing import Any
from sqlmodel import Session
from ..backend_models.base import CRUDBase

class BaseService(ABC):
    model_class = None
    data_accessor: CRUDBase = None

    def get(self, session: Session, id: int) -> Any:
        return self.data_accessor.get(session, id)

    def get_all(self, session: Session) -> list:
        return self.data_accessor.get_all(session)

    def create(self, entity: Any, session: Session):
        return self.data_accessor.create(session, entity)

    def update(
        self,
        entity: Any,
        session: Session,
    ):
        return self.data_accessor.update(session, entity)

    def delete(self, session: Session, entity: Any):
        return self.data_accessor.delete(session, entity.id)

    def delete_many(self, session: Session, instances: list, count: int) -> bool:
        if not instances:
            return False

        if count < 0:
            count = len(instances)

        to_delete = instances[:count]

        self.data_accessor.delete_many(session, to_delete)
        return True