import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from backend.app.backend_models.ingredient import IngredientCRUD
from backend.app.backend_models.expansion import expansions
from backend.app.models import Expansion
from backend.app.backend_models.recipe_ingredient import RecipeIngredientCRUD
from backend.app.models import Ingredient

def test_crud_create_leaves_commit_to_caller(
    test_engine,
):
    with Session(test_engine) as session:
        crud = IngredientCRUD(Ingredient)
        ingredient = Ingredient(name="Temporary")
        crud.create(session, ingredient)

        assert ingredient.id is not None
        assert crud.get(session, ingredient.id) is ingredient

        session.rollback()

    with Session(test_engine) as session:
        assert IngredientCRUD(Ingredient).get_all(session) == []

def test_crud_update_and_delete_can_be_rolled_back(
    test_engine,
):
    with Session(test_engine) as session:
        crud = IngredientCRUD(Ingredient)
        ingredient = Ingredient(name="Original")
        crud.create(session, ingredient)
        session.commit()
        ingredient_id = ingredient.id

        ingredient.name = "Changed"
        crud.update(session, ingredient)
        session.flush()
        session.rollback()

        assert crud.get(session, ingredient_id).name == "Original"

        crud.delete(session, ingredient_id)
        session.flush()
        session.rollback()

        assert crud.get(session, ingredient_id).name == "Original"

def test_recipe_update_rolls_back_links_and_new_ingredients(
    client,
    catalog,
    monkeypatch,
):
    response = client.post(
        "/recipes/",
        json={
            "name": "Original Recipe",
            "profession_id": catalog["alchemy"],
            "expansion_id": catalog["midnight"],
            "ingredients": [{"name": "Original Herb", "amount_required": 2}],
        },
    )
    assert response.status_code == 201
    original = response.json()
    recipe_id = original["id"]
    create_link = RecipeIngredientCRUD.create

    def fail_after_link_creation(
        self,
        session,
        record,
    ):
        create_link(
            self,
            session,
            record,
        )
        raise IntegrityError(
            "injected test failure",
            {},
            Exception("rollback test"),
        )

    monkeypatch.setattr(
        RecipeIngredientCRUD,
        "create",
        fail_after_link_creation,
    )
    response = client.patch(
        f"/recipes/{recipe_id}",
        json={
            "name": "Changed Recipe",
            "ingredients": [{"name": "Rollback Herb", "amount_required": 3}],
        },
    )

    assert response.status_code == 409
    assert client.get(f"/recipes/{recipe_id}").json() == original
    assert client.get("/ingredients/?search=Rollback%20Herb").json() == []

def test_recipe_management_still_uses_shared_ingredients(
    client,
    catalog,
):
    response = client.post("/ingredients/", json={"name": " Shared Herb "})
    assert response.status_code == 200
    ingredient_id = response.json()["id"]

    response = client.post(
        "/recipes/",
        json={
            "name": "Test Recipe",
            "profession_id": catalog["alchemy"],
            "expansion_id": catalog["midnight"],
            "ingredients": [{"name": "shared herb", "amount_required": 2}],
        },
    )
    assert response.status_code == 201
    recipe = response.json()
    recipe_id = recipe["id"]
    assert recipe["ingredients"][0]["ingredient"]["id"] == ingredient_id

    response = client.patch(f"/recipes/{recipe_id}", json={"ingredients": [{"ingredient_id": ingredient_id, "amount_required": 5}]})
    assert response.status_code == 200
    assert response.json()["ingredients"][0]["amount_required"] == 5

    response = client.patch(f"/recipes/{recipe_id}/profit", json={"profit_per_craft": 150})
    assert response.status_code == 200
    assert response.json()["profit_per_craft"] == 150

    response = client.delete(f"/recipes/{recipe_id}")
    assert response.status_code == 204
    assert client.get("/ingredients/?search=shared").json()[0]["id"] == ingredient_id

def test_expansion_management_and_guards_survive_refactor(
    client,
    catalog,
):
    response = client.post("/expansions/", json={"name": " Added "})
    assert response.status_code == 201
    expansion_id = response.json()["id"]
    assert client.post("/expansions/", json={"name": "added"}).status_code == 409

    response = client.patch(f"/expansions/{expansion_id}", json={"name": "Renamed"})
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"

    response = client.patch("/settings/", json={"current_expansion_id": expansion_id})
    assert response.status_code == 200
    assert response.json()["current_expansion"]["name"] == "Renamed"
    assert client.delete(f"/expansions/{expansion_id}").status_code == 409
    assert client.delete(f"/expansions/{catalog['midnight']}").status_code == 409

    response = client.patch("/settings/", json={"current_expansion_id": catalog["midnight"]})
    assert response.status_code == 200
    assert client.delete(f"/expansions/{expansion_id}").status_code == 204

def test_crud_delete_many_rolls_back_earlier_deletions_on_failure(test_engine, catalog):
    with Session(test_engine) as session:
        available = Expansion(name="Available")
        expansions.create(session, available)
        session.commit()
        available_id = available.id
        blocked = expansions.get(session, catalog["midnight"])

        with pytest.raises(IntegrityError):
            expansions.delete_many(session, [available, blocked])

        assert expansions.get(session, available_id) is not None
        assert expansions.get(session, catalog["midnight"]) is not None
