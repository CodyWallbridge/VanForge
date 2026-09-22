from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from ..auth import AuthenticatedUser
from ..backend_models.account import accounts
from ..database import engine
from ..models import Account, DeletedAuthUser
from .base import BaseService

class AccountService(BaseService):
    model_class = Account
    data_accessor = accounts

    def __init__(self, engine_override=None):
        self.engine = engine_override or engine

    def get_auth_user_created_at(
        self,
        session: Session,
        auth_user_id: str,
    ):
        return session.execute(
            text('SELECT "createdAt" FROM neon_auth."user" WHERE CAST(id AS text) = :auth_user_id'),
            {"auth_user_id": auth_user_id},
        ).scalar_one_or_none()

    def get_or_create_account(
        self,
        authenticated_user: AuthenticatedUser,
    ):
        with Session(self.engine) as session:
            deleted_user = session.get(DeletedAuthUser, authenticated_user.id)

            if deleted_user is not None:
                auth_user_created_at = self.get_auth_user_created_at(session, authenticated_user.id)
                user_was_recreated = auth_user_created_at is not None and (
                    deleted_user.deleted_at is None or auth_user_created_at > deleted_user.deleted_at
                )

                if not user_was_recreated:
                    raise HTTPException(status_code=403, detail="This VanForge account was deleted. Sign up again to create a new account")

                session.delete(deleted_user)
                session.flush()

            account = self.data_accessor.get_by_auth_user_id(session, authenticated_user.id)

            if account is None:
                account = Account(
                    auth_user_id=authenticated_user.id,
                    email=authenticated_user.email,
                    role="user",
                )

                try:
                    account = self.create(entity=account, session=session)
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    account = self.data_accessor.get_by_auth_user_id(session, authenticated_user.id)

                    if account is None:
                        raise

                session.refresh(account)

                return account

            if authenticated_user.email is not None and account.email != authenticated_user.email:
                account.email = authenticated_user.email
                account = self.update(entity=account, session=session)

                session.commit()
                session.refresh(account)

            return account

    def get_accounts(self):
        with Session(self.engine) as session:
            return self.get_all(session)

    def update_role(
        self,
        account_id: int,
        role: str,
    ):
        with Session(self.engine) as session:
            account = self.get(session, account_id)

            if account is None:
                raise HTTPException(status_code=404, detail="Account not found")

            if account.role == "admin" and role != "admin":
                if self.data_accessor.count_admins(session) <= 1:
                    raise HTTPException(status_code=400, detail="The final administrator cannot be demoted")

            account.role = role
            account = self.update(entity=account, session=session)

            session.commit()
            session.refresh(account)

            return account

    def delete_account(
        self,
        current_account_id: int,
        account_id: int,
    ):
        if current_account_id == account_id:
            raise HTTPException(status_code=400, detail="You cannot delete your active account")

        with Session(self.engine) as session:
            account = self.get(session, account_id)

            if account is None:
                raise HTTPException(status_code=404, detail="Account not found")

            if account.role == "admin" and self.data_accessor.count_admins(session) <= 1:
                raise HTTPException(status_code=400, detail="The final administrator cannot be deleted")

            deleted_user = DeletedAuthUser(auth_user_id=account.auth_user_id)
            session.add(deleted_user)
            self.delete(session, account)
            session.commit()

