from fastapi import HTTPException
from ..models import Ingredient, RecipeIngredient
from .common import clean_name, find_named, require_record

def resolve_ingredients(
    session,
    entries,
):
    resolved = []
    seen_ids = set()
    seen_names = set()

    for entry in entries:
        if entry.ingredient_id is not None:
            ingredient = require_record(session, Ingredient, entry.ingredient_id)

            name = ingredient.name.strip()
        else:
            name = clean_name(entry.name)
            ingredient = find_named(session, Ingredient, name)

        key = name.casefold()

        if key in seen_names or (ingredient is not None and ingredient.id in seen_ids):
            raise HTTPException(status_code=400, detail="Each ingredient can only appear once in a recipe")

        seen_names.add(key)

        if ingredient is not None:
            seen_ids.add(ingredient.id)

        resolved.append((ingredient, name, entry.amount_required))

    return resolved

def add_ingredient_links(
    session,
    recipe_id,
    resolved,
):
    for ingredient, name, amount in resolved:
        if ingredient is None:
            ingredient = Ingredient(name=name)
            session.add(ingredient)
            session.flush()

        link = RecipeIngredient(
            recipe_id=recipe_id,
            ingredient_id=ingredient.id,
            amount_required=amount,
        )
        session.add(link)
