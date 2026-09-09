from typing import Generic, Optional, Type, TypeVar
from sqlmodel import Session, select
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class CRUDBase(Generic[T]):
    model: Type[T]

    def __init__(self, model: Type[T]):
        self.model = model

    def create(self, session: Session, obj: T) -> T:
        if obj is None:
            return None

        session.add(obj)
        session.flush()
        session.refresh(obj)

        return obj

    def create_many(self, session: Session, objs: list[T]) -> list[T]:
        session.add_all(objs)
        for obj in objs:
            session.flush()
            session.refresh(obj)

        return objs

    def update(self, session: Session, obj: T) -> Optional[T]:
        if not obj:
            return None

        db_obj = session.get(self.model, obj.id)
        if not db_obj:
            return None

        for field, value in obj.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)

        session.flush()
        session.refresh(db_obj)
        return db_obj

    def delete(self, session: Session, id: int) -> None:
        db_obj = session.get(self.model, id)
        if db_obj:
            session.delete(db_obj)
            session.flush()

    def delete_many(self, session: Session, objects: list[T]) -> None:
        try:
            for obj in objects:
                session.delete(obj)
                session.flush()

        except Exception as e:
            session.rollback()
            raise e

    def get(self, session: Session, record_id) -> Optional[T]:
        return session.get(self.model, record_id)

    def get_all(self, session: Session) -> list[T]:
        return session.exec(
            select(self.model).order_by(self.model.id),
        ).all()

    def truncate(self, session: Session) -> None:
        results = self.get_all(session)
        for result in results:
            self.delete(session, result.id)