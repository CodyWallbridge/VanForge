import pytest
from sqlmodel import Session
from backend.app.models import AppSettings, Character, CharacterRecipe, Ingredient, Recipe, RecipeIngredient

@pytest.fixture
def optimization_catalog(test_engine, catalog):
    with Session(test_engine) as session:
        first = Character(
            name="First",
            profession1_id=catalog["alchemy"],
            profession2_id=catalog["blacksmithing"],
            concentration=10,
        )
        second = Character(
            name="Second",
            profession1_id=catalog["alchemy"],
            profession2_id=catalog["blacksmithing"],
            concentration=5,
        )
        empty = Character(
            name="Empty",
            profession1_id=catalog["alchemy"],
            profession2_id=catalog["blacksmithing"],
            concentration=0,
        )
        material = Ingredient(name="Shared Material")
        session.add_all([first, second, empty, material])
        session.flush()
        recipe_ids = []

        # Include recipes that must be excluded for expansion, profession,
        # missing knowledge, zero profit, and negative profit.
        specs = [
            (catalog["alchemy"], catalog["midnight"], 12, 6),
            (catalog["alchemy"], catalog["midnight"], 7, 4),
            (catalog["blacksmithing"], catalog["midnight"], 11, 5),
            (catalog["alchemy"], catalog["future"], 10000, 1),
            (catalog["tailoring"], catalog["midnight"], 10000, 1),
            (catalog["alchemy"], catalog["midnight"], 10000, None),
            (catalog["alchemy"], catalog["midnight"], 0, 1),
            (catalog["alchemy"], catalog["midnight"], -10, 1),
        ]

        for index, (profession, expansion, profit, cost) in enumerate(specs):
            recipe = Recipe(
                name=f"Recipe {index}",
                profession_id=profession,
                expansion_id=expansion,
                profit_per_craft=profit,
            )
            session.add(recipe)
            session.flush()
            recipe_ids.append(recipe.id)
            link = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=material.id,
                amount_required=2,
            )
            session.add(link)

            if cost is not None:
                for character in [first, second]:
                    assignment = CharacterRecipe(
                        character_id=character.id,
                        recipe_id=recipe.id,
                        concentration_cost=cost,
                    )
                    session.add(assignment)

        session.commit()

        return {
            "first": first.id,
            "second": second.id,
            "empty": empty.id,
            "recipes": recipe_ids,
        }

def test_multiple_characters_optimize_and_feed_manual_planner(
    client,
    optimization_catalog,
    test_engine,
):
    ids = [optimization_catalog["first"], optimization_catalog["second"]]
    response = client.post("/planner/optimize", json={"character_ids": ids})

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["total_profit"] == 59
    assert [item["profit"] for item in result["characters"]] == [41, 18]
    assert [item["character_id"] for item in result["characters"]] == ids
    assert len(result["crafts"]) == 5

    for character in result["characters"]:
        assert len(character["professions"]) == 2
        for profession in character["professions"]:
            assert profession["concentration_used"] >= 0
            assert profession["concentration_remaining"] >= 0

    manual = client.post("/planner/", json=result["crafts"])
    assert manual.status_code == 200, manual.text
    assert manual.json() == {"Shared Material": 12}

    with Session(test_engine) as session:
        assert session.get(Character, ids[0]).concentration == 10
        assert session.get(Character, ids[1]).concentration == 5

    repeated = client.post("/planner/optimize", json={"character_ids": ids})
    assert repeated.json() == result

def test_selected_subset_and_empty_character(client, optimization_catalog):
    character_id = optimization_catalog["empty"]
    response = client.post("/planner/optimize", json={"character_ids": [character_id]})

    assert response.status_code == 200
    result = response.json()
    assert result["crafts"] == []
    assert result["total_profit"] == 0
    assert len(result["characters"]) == 1
    assert result["characters"][0]["character_id"] == character_id
    assert len(result["characters"][0]["professions"]) == 2

@pytest.mark.parametrize("ids, status", [([], 422), ([1, 1], 422), ([999999], 404)])
def test_invalid_selection(
    client,
    ids,
    status,
):
    response = client.post("/planner/optimize", json={"character_ids": ids})

    assert response.status_code == status

def test_missing_selected_expansion(client, character, test_engine):
    with Session(test_engine) as session:
        settings = session.get(AppSettings, 1)
        session.delete(settings)
        session.commit()

    response = client.post("/planner/optimize", json={"character_ids": [character["id"]]})

    assert response.status_code == 400
