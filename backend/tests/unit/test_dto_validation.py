import pytest
from pydantic import ValidationError

from backend.app.dtos import CharacterCreate, CharacterPlanItem, CharacterRecipeCreate
from backend.app.dtos import IngredientCreate, RecipeCreate, RecipeIngredientCreate, RecipeProfitUpdate

@pytest.mark.parametrize("concentration", [-1, 1001])
def test_character_rejects_out_of_range_concentration(
    concentration,
):
    with pytest.raises(ValidationError) as error:
        CharacterCreate(
            name="Test",
            profession1_id=1,
            profession2_id=2,
            concentration=concentration,
        )

    assert error.value.errors()[0]["loc"] == ("concentration",)

@pytest.mark.parametrize("concentration", [0, 500, 1000])
def test_character_accepts_valid_concentration(
    concentration,
):
    character = CharacterCreate(
        name="Test",
        profession1_id=1,
        profession2_id=2,
        concentration=concentration,
    )

    assert character.concentration == concentration

def test_character_defaults_to_full_concentration():
    character = CharacterCreate(
        name="Test",
        profession1_id=1,
        profession2_id=2,
    )

    assert character.concentration == 1000

@pytest.mark.parametrize(
    "model, fields",
    [
        (CharacterCreate, {"profession1_id": 1, "profession2_id": 2}),
        (IngredientCreate, {}),
    ],
)
def test_creation_rejects_empty_name(
    model,
    fields,
):
    with pytest.raises(ValidationError) as error:
        model(name="", **fields)

    assert error.value.errors()[0]["loc"] == ("name",)

@pytest.mark.parametrize("cost", [-1, 0])
def test_learned_recipe_rejects_nonpositive_cost(
    cost,
):
    with pytest.raises(ValidationError) as error:
        CharacterRecipeCreate(recipe_id=1, concentration_cost=cost)

    assert error.value.errors()[0]["loc"] == ("concentration_cost",)

def test_learned_recipe_accepts_positive_cost():
    recipe = CharacterRecipeCreate(recipe_id=1, concentration_cost=250)

    assert recipe.concentration_cost == 250

@pytest.mark.parametrize("amount", [-1, 0])
def test_ingredient_rejects_nonpositive_quantity(
    amount,
):
    with pytest.raises(ValidationError) as error:
        RecipeIngredientCreate(ingredient_id=1, amount_required=amount)

    assert error.value.errors()[0]["loc"] == ("amount_required",)

def test_ingredient_accepts_positive_quantity():
    ingredient = RecipeIngredientCreate(ingredient_id=1, amount_required=1)

    assert ingredient.amount_required == 1

@pytest.mark.parametrize("crafts", [-1, 1.5])
def test_plan_rejects_negative_or_fractional_crafts(
    crafts,
):
    with pytest.raises(ValidationError) as error:
        CharacterPlanItem(character_id=1, recipe_id=1, crafts=crafts)

    assert error.value.errors()[0]["loc"] == ("crafts",)

@pytest.mark.parametrize("crafts", [0, 1, 4])
def test_plan_accepts_nonnegative_whole_crafts(
    crafts,
):
    item = CharacterPlanItem(character_id=1, recipe_id=1, crafts=crafts)

    assert item.crafts == crafts

@pytest.mark.parametrize("profit", [-150, 0, 150])
def test_profit_allows_losses_zero_and_gains(
    profit,
):
    update = RecipeProfitUpdate(profit_per_craft=profit)

    assert update.profit_per_craft == profit

def test_profit_rejects_fractional_gold():
    with pytest.raises(ValidationError) as error:
        RecipeProfitUpdate(profit_per_craft=1.5)

    assert error.value.errors()[0]["loc"] == ("profit_per_craft",)

def test_recipe_creation_validates_nested_ingredient_quantities():
    with pytest.raises(ValidationError) as error:
        RecipeCreate(
            name="Test Recipe",
            profession_id=1,
            expansion_id=1,
            ingredients=[{"ingredient_id": 1, "amount_required": 0}],
        )

    assert error.value.errors()[0]["loc"] == ("ingredients", 0, "amount_required")
