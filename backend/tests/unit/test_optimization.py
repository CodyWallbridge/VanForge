from itertools import product
from random import Random
import pytest
from pydantic import ValidationError
from backend.app.dtos import OptimizationRequest
from backend.app.services.optimization import optimize_crafts

def test_mixed_recipes_beat_best_profit_ratio():
    # The 6-cost recipe has the best ratio, but two 5-cost crafts earn more.
    quantities, profit, used = optimize_crafts(10, [(1, 6, 12), (2, 5, 9)])

    assert quantities == {2: 2}
    assert profit == 18
    assert used == 10

def test_smaller_craft_fills_remaining_budget():
    quantities, profit, used = optimize_crafts(10, [(1, 6, 12), (2, 4, 7)])

    assert quantities == {1: 1, 2: 1}
    assert profit == 19
    assert used == 10

def test_equal_profit_prefers_less_concentration():
    quantities, profit, used = optimize_crafts(10, [(1, 10, 20), (2, 9, 20)])

    assert quantities == {2: 1}
    assert profit == 20
    assert used == 9

@pytest.mark.parametrize("budget, options", [(0, [(1, 1, 10)]), (10, []), (10, [(1, 1, 0), (2, 1, -5)]), (10, [(1, 11, 20)])])
def test_no_profitable_feasible_crafts(budget, options):
    assert optimize_crafts(budget, options) == ({}, 0, 0)

@pytest.mark.parametrize("cost", [0, -1])
def test_invalid_cost_rejected(cost):
    with pytest.raises(ValueError):
        optimize_crafts(10, [(1, cost, 10)])

@pytest.mark.parametrize("budget", [-1, 1001])
def test_invalid_budget_rejected(budget):
    with pytest.raises(ValueError):
        optimize_crafts(budget, [])

def test_exact_solution_matches_exhaustive_enumeration():
    for first_cost, second_cost in product(range(1, 5), repeat=2):
        for first_profit, second_profit in product([-1, 0, 3, 5], repeat=2):
            for budget in range(9):
                options = [(1, first_cost, first_profit), (2, second_cost, second_profit)]
                quantities, profit, used = optimize_crafts(budget, options)
                expected_profit = 0
                expected_used = 0

                for first_count in range(budget // first_cost + 1):
                    for second_count in range(budget // second_cost + 1):
                        cost = first_count * first_cost + second_count * second_cost
                        value = first_count * first_profit + second_count * second_profit

                        if cost > budget:
                            continue

                        if value > expected_profit or (value == expected_profit and cost < expected_used):
                            expected_profit = value
                            expected_used = cost

                assert (profit, used) == (expected_profit, expected_used)
                first_count = quantities.get(1, 0)
                second_count = quantities.get(2, 0)
                assert first_count * first_cost + second_count * second_cost == used
                assert first_count * first_profit + second_count * second_profit == profit

@pytest.mark.parametrize("ids", [[], [1, 1]])
def test_selection_rejects_empty_or_duplicate_ids(ids):
    with pytest.raises(ValidationError):
        OptimizationRequest(character_ids=ids)


def test_lower_ratio_recipe_wins_when_high_ratio_craft_leaves_budget_unused():
    quantities, profit, used = optimize_crafts(1000, [(1, 505, 2525), (2, 250, 1000)])

    assert quantities == {2: 4}
    assert profit == 4000
    assert used == 1000

def test_best_plan_mixes_300_and_200_cost_recipes():
    quantities, profit, used = optimize_crafts(1000, [(1, 300, 1000), (2, 200, 650)])

    assert quantities == {1: 2, 2: 2}
    assert profit == 3300
    assert used == 1000

def test_full_budget_can_combine_expensive_and_small_crafts():
    quantities, profit, used = optimize_crafts(1000, [(1, 997, 1100), (2, 1, 1)])

    assert quantities == {1: 1, 2: 3}
    assert profit == 1103
    assert used == 1000

def test_randomized_combinations_match_independent_exhaustive_search():
    random = Random(2417)

    for _ in range(300):
        budget = random.randint(0, 18)
        option_count = random.randint(1, 4)
        options = []

        for recipe_id in range(1, option_count + 1):
            cost = random.randint(2, 10)
            profit = random.randint(-5, 25)
            options.append((recipe_id, cost, profit))

        expected_profit = 0
        expected_used = 0

        def search(index: int, used: int, profit: int):
            nonlocal expected_profit, expected_used

            if index == len(options):
                if profit > expected_profit or (profit == expected_profit and used < expected_used):
                    expected_profit = profit
                    expected_used = used

                return

            _, cost, value = options[index]
            max_count = (budget - used) // cost

            for count in range(max_count + 1):
                search(
                    index + 1,
                    used + count * cost,
                    profit + count * value,
                )

        search(0, 0, 0)
        quantities, profit, used = optimize_crafts(budget, options)
        actual_used = 0
        actual_profit = 0

        for recipe_id, cost, value in options:
            count = quantities.get(recipe_id, 0)
            actual_used += count * cost
            actual_profit += count * value

        assert (profit, used) == (expected_profit, expected_used)
        assert actual_used == used
        assert actual_profit == profit
