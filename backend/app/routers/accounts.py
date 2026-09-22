from fastapi import APIRouter, Depends, Response
from ..dependencies import get_current_account, require_admin
from ..dtos import AccountRead, AccountRoleUpdate
from ..models import Account
from ..services.accounts import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])
account_service = AccountService()

@router.get("/me", response_model=AccountRead)
def get_account(account: Account = Depends(get_current_account)):
    return account

@router.get("/", response_model=list[AccountRead])
def get_accounts(account: Account = Depends(require_admin)):
    return account_service.get_accounts()

@router.patch("/{account_id}/role", response_model=AccountRead)
def update_account_role(account_id: int, role_data: AccountRoleUpdate, account: Account = Depends(require_admin)):
    return account_service.update_role(account_id, role_data.role)

@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, account: Account = Depends(require_admin)):
    account_service.delete_account(account.id, account_id)

    return Response(status_code=204)
