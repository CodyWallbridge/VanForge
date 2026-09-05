import pytest
from pydantic import ValidationError

from backend.app.dtos import CharacterCreate, CharacterPlanItem, CharacterRecipeCreate
from backend.app.dtos import IngredientCreate, IngredientRead, PlanItem, RecipeCreate
from backend.app.dtos import RecipeIngredientCreate, RecipeIngredientRead, RecipeProfitUpdate, RecipeRead

DTO_CASES = [
    (CharacterCreate, {"name": "Vandredor", "profession1_id": 1, "profession2_id": 2}, {"concentration": 1000}),
    (CharacterPlanItem, {"character_id": 1, "recipe_id": 2, "crafts": 4}, {}),
    (CharacterRecipeCreate, {"recipe_id": 2, "concentration_cost": 250}, {}),
    (IngredientCreate, {"name": "Argentleaf"}, {}),
    (IngredientRead, {"id": 1, "name": "Argentleaf"}, {}),
    (PlanItem, {"recipe_id": 2, "crafts": 4}, {}),
    (RecipeCreate, {"name": "Flask", "profession_id": 1, "expansion_id": 1, "ingredients": [{"ingredient_id": 1, "amount_required": 8}]}, {"profit_per_craft": 0}),
    (RecipeIngredientCreate, {"ingredient_id": 1, "amount_required": 8}, {}),
    (RecipeIngredientRead, {"amount_required": 8, "ingredient": {"id": 1, "name": "Argentleaf"}}, {}),
    (RecipeProfitUpdate, {"profit_per_craft": -50}, {}),
    (RecipeRead, {"id": 2, "name": "Flask", "profession_id": 1, "expansion_id": 1}, {"profit_per_craft": 0, "ingredients": []}),
]

@pytest.mark.parametrize(
    "model, payload, defaults",
    DTO_CASES,
    ids=[model.__name__ for model, _, _ in DTO_CASES],
)
def test_dto_valid_payload_and_serialization(
    model,
    payload,
    defaults,
):
    dto = model.model_validate(payload)

    assert dto.model_dump() == payload | defaults
    assert model.model_validate_json(
        dto.model_dump_json()
    ) == dto

@pytest.mark.parametrize(
    "model, payload, missing_field",
    [
        (model, payload, field)
        for model, payload, _ in DTO_CASES
        for field in payload
    ],
    ids=[
        f"{model.__name__}-{field}"
        for model, payload, _ in DTO_CASES
        for field in payload
    ],
)
def test_dto_rejects_missing_required_field(
    model,
    payload,
    missing_field,
):
    incomplete = payload.copy()
    del incomplete[missing_field]

    with pytest.raises(ValidationError) as error:
        model.model_validate(incomplete)

    assert any(
        item["loc"] == (missing_field,) and item["type"] == "missing"
        for item in error.value.errors()
    )

def test_recipe_create_builds_typed_ingredients():
    recipe = RecipeCreate(
        name="Flask",
        profession_id=1,
        expansion_id=1,
        ingredients=[{"ingredient_id": 1, "amount_required": 8}],
    )

    assert isinstance(recipe.ingredients[0], RecipeIngredientCreate)
    assert recipe.ingredients[0].amount_required == 8

def test_recipe_read_serializes_nested_ingredients():
    payload = {
        "id": 2,
        "name": "Flask",
        "profession_id": 1,
        "expansion_id": 1,
        "profit_per_craft": 150,
        "ingredients": [
            {"amount_required": 8, "ingredient": {"id": 1, "name": "Argentleaf"}},
        ],
    }
    recipe = RecipeRead.model_validate(payload)

    assert isinstance(recipe.ingredients[0], RecipeIngredientRead)
    assert isinstance(recipe.ingredients[0].ingredient, IngredientRead)
    assert recipe.model_dump() == payload

def test_recipe_read_default_ingredient_lists_are_independent():
    first = RecipeRead(id=1, name="First", profession_id=1, expansion_id=1)
    second = RecipeRead(id=2, name="Second", profession_id=1, expansion_id=1)
    ingredient = RecipeIngredientRead(
        amount_required=8,
        ingredient=IngredientRead(id=1, name="Argentleaf"),
    )
    first.ingredients.append(ingredient)

    assert second.ingredients == []

def test_recipe_read_rejects_incomplete_nested_ingredient():
    with pytest.raises(ValidationError) as error:
        RecipeRead(
            id=2,
            name="Flask",
            profession_id=1,
            expansion_id=1,
            ingredients=[{"amount_required": 8, "ingredient": {"id": 1}}],
        )

    assert error.value.errors()[0]["loc"] == ("ingredients", 0, "ingredient", "name")

def test_recipe_ingredient_read_rejects_invalid_quantity_type():
    with pytest.raises(ValidationError) as error:
        RecipeIngredientRead(
            amount_required="not a number",
            ingredient=IngredientRead(id=1, name="Argentleaf"),
        )

    assert error.value.errors()[0]["loc"] == ("amount_required",)

@pytest.mark.parametrize("crafts", [1.5, "not a number"])
def test_plan_item_rejects_invalid_craft_type(
    crafts,
):
    with pytest.raises(ValidationError) as error:
        PlanItem(recipe_id=1, crafts=crafts)

    assert error.value.errors()[0]["loc"] == ("crafts",)
