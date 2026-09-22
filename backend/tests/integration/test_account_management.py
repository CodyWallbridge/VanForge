import pytest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from fastapi import HTTPException
from sqlmodel import Session, select
from backend.app import main
from backend.app.auth import AuthenticatedUser
from backend.app.backend_models.account import AccountCRUD
from backend.app.dependencies import get_current_account
from backend.app.models import Account, AppSettings, Character, RecipeProfit
from backend.app.services.accounts import AccountService

def test_account_bootstrap_handles_concurrent_first_requests(
    monkeypatch,
    test_engine,
):
    barrier = Barrier(2)
    original_get = AccountCRUD.get_by_auth_user_id

    def synchronized_get(
        self,
        session,
        auth_user_id,
    ):
        account = original_get(self, session, auth_user_id)

        if account is None:
            barrier.wait()

        return account

    monkeypatch.setattr(AccountCRUD, "get_by_auth_user_id", synchronized_get)
    account_service = AccountService(engine_override=test_engine)
    authenticated_user = AuthenticatedUser(id="concurrent-user", email="concurrent@example.com")

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(account_service.get_or_create_account, [authenticated_user, authenticated_user]))

    assert results[0].id == results[1].id

    with Session(test_engine) as session:
        accounts = session.exec(
            select(Account)
            .where(Account.auth_user_id == authenticated_user.id),
        ).all()

        assert len(accounts) == 1

def test_recipe_profit_is_private_to_each_account(
    client,
    catalog,
    test_engine,
):
    admin_override = main.app.dependency_overrides[get_current_account]
    response = client.patch(
        f"/recipes/{catalog['flask']}/profit",
        json={"profit_per_craft": 100},
    )
    assert response.status_code == 200

    with Session(test_engine) as session:
        other_account = Account(
            auth_user_id="profit-user",
            email="profit@example.com",
            role="user",
        )
        session.add(other_account)
        session.commit()
        session.refresh(other_account)

    main.app.dependency_overrides[get_current_account] = lambda: other_account

    try:
        response = client.patch(
            f"/recipes/{catalog['flask']}/profit",
            json={"profit_per_craft": 40},
        )
        assert response.status_code == 200
        assert response.json()["profit_per_craft"] == 40
    finally:
        main.app.dependency_overrides[get_current_account] = admin_override

    response = client.get(f"/recipes/{catalog['flask']}")
    assert response.status_code == 200
    assert response.json()["profit_per_craft"] == 100

def test_deleting_local_account_cascades_owned_data(
    catalog,
    test_engine,
):
    with Session(test_engine) as session:
        account = Account(
            auth_user_id="delete-user",
            email="delete@example.com",
            role="user",
        )
        session.add(account)
        session.flush()

        settings = AppSettings(
            account_id=account.id,
            current_expansion_id=catalog["midnight"],
        )
        character = Character(
            account_id=account.id,
            name="Delete Me",
            profession1_id=catalog["alchemy"],
            profession2_id=catalog["tailoring"],
            concentration=1000,
        )
        profit = RecipeProfit(
            account_id=account.id,
            recipe_id=catalog["flask"],
            profit_per_craft=25,
        )
        session.add_all([settings, character, profit])
        session.commit()
        account_id = account.id

    account_service = AccountService(engine_override=test_engine)
    account_service.delete_account(
        catalog["account"],
        account_id,
    )

    with Session(test_engine) as session:
        assert session.get(Account, account_id) is None
        assert session.exec(
            select(AppSettings)
            .where(AppSettings.account_id == account_id),
        ).first() is None
        assert session.exec(
            select(Character)
            .where(Character.account_id == account_id),
        ).first() is None
        assert session.exec(
            select(RecipeProfit)
            .where(RecipeProfit.account_id == account_id),
        ).first() is None

    recreated = account_service.get_or_create_account(
        AuthenticatedUser(id="delete-user", email="delete@example.com"),
    )

    assert recreated.id != account_id
    assert recreated.role == "user"

def test_active_account_cannot_delete_itself(
    catalog,
    test_engine,
):
    account_service = AccountService(engine_override=test_engine)

    with pytest.raises(HTTPException) as error:
        account_service.delete_account(catalog["account"], catalog["account"])

    assert error.value.status_code == 400
    assert error.value.detail == "You cannot delete your active account"

def test_final_admin_cannot_be_demoted(
    catalog,
    test_engine,
):
    account_service = AccountService(engine_override=test_engine)

    with pytest.raises(HTTPException) as error:
        account_service.update_role(catalog["account"], "user")

    assert error.value.status_code == 400
    assert error.value.detail == "The final administrator cannot be demoted"

def test_admin_can_list_update_and_delete_other_accounts(
    client,
    test_engine,
):
    with Session(test_engine) as session:
        account = Account(
            auth_user_id="managed-user",
            email="managed@example.com",
            role="user",
        )
        session.add(account)
        session.commit()
        session.refresh(account)
        account_id = account.id

    response = client.get("/accounts/")
    assert response.status_code == 200
    assert account_id in [account["id"] for account in response.json()]

    response = client.patch(f"/accounts/{account_id}/role", json={"role": "admin"})
    assert response.status_code == 200
    assert response.json()["role"] == "admin"

    response = client.delete(f"/accounts/{account_id}")
    assert response.status_code == 204

    with Session(test_engine) as session:
        assert session.get(Account, account_id) is None
