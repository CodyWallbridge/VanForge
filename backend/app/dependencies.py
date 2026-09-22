from fastapi import Depends, HTTPException
from .auth import AuthenticatedUser, get_current_user
from .models import Account
from .services.accounts import AccountService

account_service = AccountService()

def get_current_account(authenticated_user: AuthenticatedUser = Depends(get_current_user)) -> Account:
    return account_service.get_or_create_account(authenticated_user)

def require_admin(account: Account = Depends(get_current_account)) -> Account:
    if account.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access is required")

    return account
