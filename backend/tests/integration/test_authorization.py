from backend.app import main
from backend.app.dependencies import get_current_account
from backend.app.models import Account

def test_missing_authentication_is_rejected(
    client,
):
    original_override = main.app.dependency_overrides.pop(get_current_account)

    try:
        response = client.get("/characters/")

        assert response.status_code == 401
        assert response.json() == {"detail": "Authentication is required"}
    finally:
        main.app.dependency_overrides[get_current_account] = original_override

def test_regular_account_can_read_but_cannot_change_shared_catalog_or_accounts(
    client,
):
    regular_account = Account(
        id=999,
        auth_user_id="regular-user",
        email="regular@example.com",
        role="user",
    )
    original_override = main.app.dependency_overrides[get_current_account]
    main.app.dependency_overrides[get_current_account] = lambda: regular_account

    try:
        assert client.get("/expansions/").status_code == 200
        response = client.post("/expansions/", json={"name": "Blocked Expansion"})

        assert response.status_code == 403
        assert response.json() == {"detail": "Administrator access is required"}
        assert client.post("/ingredients/", json={"name": "Blocked Ingredient"}).status_code == 403
        assert client.post("/recipes/", json={}).status_code == 403
        assert client.get("/accounts/").status_code == 403
    finally:
        main.app.dependency_overrides[get_current_account] = original_override
