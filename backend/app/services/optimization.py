def optimize_crafts(budget: int, options: list[tuple[int, int, int]]):
    """Return quantities, profit and cost for (recipe_id, cost, profit) options.

    Each DP entry is the best profit using exactly that much concentration.
    Ascending costs allow unlimited repetitions. Choosing the first maximum
    prefers less concentration when profits tie.
    """
    if budget < 0 or budget > 1000:
        raise ValueError("Concentration must be between 0 and 1000")

    for recipe_id, cost, profit in options:
        if cost <= 0:
            raise ValueError("Concentration costs must be positive")

    profits = [None] * (budget + 1)
    previous = [None] * (budget + 1)
    profits[0] = 0
    best_cost = 0

    for concentration in range(1, budget + 1):
        for recipe_id, cost, profit in options:
            if profit <= 0 or cost > concentration:
                continue

            previous_profit = profits[concentration - cost]

            if previous_profit is None:
                continue

            candidate = previous_profit + profit

            if profits[concentration] is None or candidate > profits[concentration]:
                profits[concentration] = candidate
                previous[concentration] = (recipe_id, cost)

        if profits[concentration] is not None and profits[concentration] > profits[best_cost]:
            best_cost = concentration

    quantities = {}
    remaining = best_cost

    while remaining > 0:
        recipe_id, cost = previous[remaining]
        quantities[recipe_id] = quantities.get(recipe_id, 0) + 1
        remaining -= cost

    return quantities, profits[best_cost], best_cost
