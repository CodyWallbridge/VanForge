import pytest
from pydantic import ValidationError
from backend.app.dtos import CharacterUpdate, CharacterRead, CharacterRecipeUpdate, CharacterRecipeRead
from backend.app.dtos import RecipeUpdate, RecipeIngredientCreate, ExpansionCreate, ExpansionUpdate, ExpansionRead
from backend.app.dtos import AppSettingsUpdate, AppSettingsRead, ProfessionRead

@pytest.mark.parametrize("model", [CharacterUpdate, RecipeUpdate])
def test_empty_patch_leaves_fields_unset(
    model,
):
    assert model().model_dump(exclude_unset=True) == {}

@pytest.mark.parametrize(
    "model, field",
    [(CharacterUpdate, field) for field in ["name", "profession1_id", "profession2_id", "concentration"]]
    + [(RecipeUpdate, field) for field in ["name", "profit_per_craft", "profession_id", "expansion_id", "ingredients"]],
)
def test_patch_rejects_explicit_null(
    model,
    field,
):
    with pytest.raises(ValidationError):
        model.model_validate({field: None})

@pytest.mark.parametrize("value", [-1, 1001])
def test_character_patch_rejects_invalid_concentration(
    value,
):
    with pytest.raises(ValidationError):
        CharacterUpdate(concentration=value)

@pytest.mark.parametrize("value", [0, 1000])
def test_character_patch_accepts_concentration_boundaries(
    value,
):
    patch = CharacterUpdate(concentration=value)

    assert patch.model_dump(exclude_unset=True) == {"concentration": value}

@pytest.mark.parametrize("cost", [0, -1])
def test_assignment_update_rejects_invalid_cost(
    cost,
):
    with pytest.raises(ValidationError):
        CharacterRecipeUpdate(concentration_cost=cost)

@pytest.mark.parametrize(
    "payload",
    [
        {"amount_required": 1},
        {"ingredient_id": 1, "name": "Herb", "amount_required": 1},
        {"name": "   ", "amount_required": 1},
    ],
)
def test_ingredient_requires_exactly_one_valid_reference(
    payload,
):
    with pytest.raises(ValidationError):
        RecipeIngredientCreate.model_validate(payload)

def test_inline_ingredient_name_is_trimmed():
    entry = RecipeIngredientCreate(name=" Herb ", amount_required=2)

    assert entry.name == "Herb"
    assert entry.ingredient_id is None

def test_recipe_patch_can_clear_ingredients_without_resetting_profit():
    patch = RecipeUpdate(ingredients=[])

    assert patch.model_dump(exclude_unset=True) == {"ingredients": []}

@pytest.mark.parametrize("model", [ExpansionCreate, ExpansionUpdate])
def test_expansion_rejects_empty_name(
    model,
):
    with pytest.raises(ValidationError):
        model(name="")

@pytest.mark.parametrize(
    "model, payload",
    [
        (CharacterRead, {"id": 1, "name": "Test", "profession1_id": 1, "profession2_id": 2, "concentration": 1000}),
        (CharacterRecipeRead, {"character_id": 1, "recipe_id": 2, "concentration_cost": 250}),
        (CharacterRecipeUpdate, {"concentration_cost": 250}),
        (ExpansionCreate, {"name": "Midnight"}),
        (ExpansionUpdate, {"name": "Renamed"}),
        (ExpansionRead, {"id": 1, "name": "Midnight"}),
        (ProfessionRead, {"id": 1, "name": "Alchemy"}),
        (AppSettingsUpdate, {"current_expansion_id": 1}),
        (AppSettingsRead, {"id": 1, "current_expansion_id": 1, "current_expansion": {"id": 1, "name": "Midnight"}}),
    ],
)
def test_management_dto_serialization_and_required_fields(
    model,
    payload,
):
    assert model.model_validate(payload).model_dump() == payload

    for field in payload:
        incomplete = payload.copy()
        del incomplete[field]

        with pytest.raises(ValidationError) as error:
            model.model_validate(incomplete)

        assert error.value.errors()[0]["loc"] == (field,)
