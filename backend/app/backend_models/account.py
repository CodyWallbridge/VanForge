from sqlmodel import Session, select
from ..models import Account
from .base import CRUDBase

class AccountCRUD(CRUDBase[Account]):
    def get_by_auth_user_id(
        self,
        session: Session,
        auth_user_id: str,
    ):
        return session.exec(
            select(Account).where(Account.auth_user_id == auth_user_id),
        ).first()

    def count_admins(self, session: Session) -> int:
        return len(
            session.exec(
                select(Account).where(Account.role == "admin"),
            ).all(),
        )

accounts = AccountCRUD(Account)