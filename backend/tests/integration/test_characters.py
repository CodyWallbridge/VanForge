from backend.app.backend_models.character_recipe import character_recipes
import pytest
from sqlmodel import Session, select
from backend.app.models import Character, CharacterRecipe, Recipe

def test_create_list_and_read_character(
    client,
    catalog,
    test_engine,
):
    assert client.get("/characters/").json() == []

    response = client.post("/characters/", json={"name": " Vandredor ", "profession1_id": catalog["alchemy"], "profession2_id": catalog["tailoring"]})
    assert response.status_code == 201
    character = response.json()
    assert character["name"] == "Vandredor"
    assert character["concentration"] == 1000
    assert client.get(f"/characters/{character['id']}").json() == character
    assert client.get("/characters/").json() == [character]

    with Session(test_engine) as session:
        assert session.get(Character, character["id"]).name == "Vandredor"
        assert session.connection().exec_driver_sql("PRAGMA foreign_keys").scalar() == 1

@pytest.mark.parametrize(
    "changes, status",
    [
        ({"name": "   "}, 400),
        ({"name": ""}, 422),
        ({"profession1_id": 99999}, 404),
        ({"concentration": -1}, 422),
        ({"concentration": 1001}, 422),
    ],
)
def test_invalid_character_creation_saves_nothing(
    client,
    catalog,
    changes,
    status,
):
    payload = {"name": "Test", "profession1_id": catalog["alchemy"], "profession2_id": catalog["tailoring"]}
    payload.update(changes)

    response = client.post("/characters/", json=payload)

    assert response.status_code == status
    assert client.get("/characters/").json() == []

def test_duplicate_professions_rejected_on_create_and_update(
    client,
    catalog,
    character,
):
    response = client.post("/characters/", json={"name": "Invalid", "profession1_id": catalog["alchemy"], "profession2_id": catalog["alchemy"]})
    assert response.status_code == 400

    response = client.patch(f"/characters/{character['id']}", json={"profession2_id": catalog["alchemy"]})
    assert response.status_code == 400
    assert client.get(f"/characters/{character['id']}").json() == character

@pytest.mark.parametrize("concentration", [0, 500, 1000])
def test_patch_preserves_omitted_fields(
    client,
    character,
    concentration,
):
    response = client.patch(f"/characters/{character['id']}", json={"concentration": concentration})
    expected = character.copy()
    expected["concentration"] = concentration

    assert response.status_code == 200
    assert response.json() == expected
    assert client.get(f"/characters/{character['id']}").json() == expected

def test_rename_and_empty_patch(
    client,
    character,
):
    response = client.patch(f"/characters/{character['id']}", json={"name": " Renamed "})
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"

    unchanged = client.patch(f"/characters/{character['id']}", json={})

    assert unchanged.status_code == 200
    assert unchanged.json() == response.json()

@pytest.mark.parametrize(
    "changes, status",
    [
        ({"name": "   "}, 400),
        ({"name": None}, 422),
        ({"concentration": -1}, 422),
        ({"concentration": 1001}, 422),
        ({"concentration": None}, 422),
        ({"name": "Should Not Save", "profession2_id": 99999}, 404),
    ],
)
def test_invalid_patch_preserves_character(
    client,
    character,
    changes,
    status,
):
    response = client.patch(f"/characters/{character['id']}", json=changes)

    assert response.status_code == status
    assert client.get(f"/characters/{character['id']}").json() == character

@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_missing_character_returns_404(
    client,
    method,
):
    if method == "patch":
        response = client.patch("/characters/99999", json={"name": "Missing"})
    else:
        response = client.request(method, "/characters/99999")

    assert response.status_code == 404

def test_profession_switch_preserves_assignments_and_filters_planning(
    client,
    catalog,
    character,
    test_engine,
):
    character_id = character["id"]
    recipe_id = catalog["flask"]
    response = client.post(f"/characters/{character_id}/recipes", json={"recipe_id": recipe_id, "concentration_cost": 250})
    assert response.status_code == 201

    response = client.patch(f"/characters/{character_id}", json={"profession1_id": catalog["blacksmithing"]})
    assert response.status_code == 200
    assert client.get(f"/characters/{character_id}/recipes").json() == []
    assert client.get(f"/planner/options/{character_id}").json() == []

    plan = [{"character_id": character_id, "recipe_id": recipe_id, "crafts": 1}]
    assert client.post("/planner/", json=plan).status_code == 400

    with Session(test_engine) as session:
        assert character_recipes.get_by_character_recipe(
            session,
            character_id,
            recipe_id,
        ).concentration_cost == 250

    response = client.patch(f"/characters/{character_id}", json={"profession1_id": catalog["alchemy"]})
    assert response.status_code == 200
    assert client.get(f"/characters/{character_id}/recipes").json()[0]["concentration_cost"] == 250
    assert client.get(f"/planner/options/{character_id}").json()[0]["recipe_id"] == recipe_id
    assert client.post("/planner/", json=plan).status_code == 200

def test_current_recipes_filter_selected_expansion(
    client,
    catalog,
    character,
):
    for recipe_id in [catalog["flask"], catalog["future_flask"]]:
        response = client.post(f"/characters/{character['id']}/recipes", json={"recipe_id": recipe_id, "concentration_cost": 250})
        assert response.status_code == 201

    current = client.get(f"/characters/{character['id']}/recipes").json()
    assert [entry["recipe_id"] for entry in current] == [catalog["flask"]]

    response = client.patch("/settings/", json={"current_expansion_id": catalog["future"]})
    assert response.status_code == 200
    current = client.get(f"/characters/{character['id']}/recipes").json()
    assert [entry["recipe_id"] for entry in current] == [catalog["future_flask"]]

def test_assignment_update_duplicate_and_removal(
    client,
    catalog,
    character,
    test_engine,
):
    path = f"/characters/{character['id']}/recipes"
    payload = {"recipe_id": catalog["flask"], "concentration_cost": 250}
    assert client.post(path, json=payload).status_code == 201
    assert client.post(path, json=payload).status_code == 409

    assignment_path = f"{path}/{catalog['flask']}"
    assert client.patch(assignment_path, json={"concentration_cost": 0}).status_code == 422
    response = client.patch(assignment_path, json={"concentration_cost": 200})
    assert response.status_code == 200
    assert response.json()["concentration_cost"] == 200

    response = client.delete(assignment_path)
    assert response.status_code == 204
    assert response.content == b""
    assert client.delete(assignment_path).status_code == 404

    with Session(test_engine) as session:
        assert character_recipes.get_by_character_recipe(
            session,
            character["id"],
            catalog["flask"],
        ) is None
        assert session.get(Recipe, catalog["flask"]) is not None

@pytest.mark.parametrize("case, status", [("wrong_profession", 400), ("missing_recipe", 404), ("invalid_cost", 422)])
def test_invalid_assignment_saves_nothing(
    client,
    catalog,
    character,
    case,
    status,
):
    payload = {"recipe_id": catalog["flask"], "concentration_cost": 250}
    if case == "wrong_profession":
        payload["recipe_id"] = catalog["alloy"]
    elif case == "missing_recipe":
        payload["recipe_id"] = 99999
    else:
        payload["concentration_cost"] = 0

    response = client.post(f"/characters/{character['id']}/recipes", json=payload)

    assert response.status_code == status
    assert client.get(f"/characters/{character['id']}/recipes").json() == []

def test_delete_character_cascades_only_its_assignments(
    client,
    catalog,
    character,
    test_engine,
):
    response = client.post("/characters/", json={"name": "Other", "profession1_id": catalog["alchemy"], "profession2_id": catalog["tailoring"]})
    assert response.status_code == 201
    other_id = response.json()["id"]

    for character_id in [character["id"], other_id]:
        response = client.post(f"/characters/{character_id}/recipes", json={"recipe_id": catalog["flask"], "concentration_cost": 250})
        assert response.status_code == 201

    response = client.delete(f"/characters/{character['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/characters/{character['id']}").status_code == 404
    assert client.get(f"/characters/{other_id}").status_code == 200

    with Session(test_engine) as session:
        assert character_recipes.get_by_character_recipe(
            session,
            character["id"],
            catalog["flask"],
        ) is None
        assert character_recipes.get_by_character_recipe(
            session,
            other_id,
            catalog["flask"],
        ) is not None
        assert session.get(Recipe, catalog["flask"]) is not None
        assert session.connection().exec_driver_sql("PRAGMA foreign_key_check").all() == []
