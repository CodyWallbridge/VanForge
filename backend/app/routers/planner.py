from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from ..models import AppSettings, Recipe, RecipeIngredient, Character, CharacterRecipe
from ..dtos import CharacterPlanItem
from ..database import get_session

router = APIRouter(
    prefix="/planner",
    tags=["planner"]
)

@router.get("/options/{character_id}")
def get_options(character_id: int, session: Session = Depends(get_session)):
    character = session.get(Character, character_id)

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    settings = session.get(AppSettings, 1)

    if settings is None:
        raise HTTPException(
            status_code=400,
            detail="Select an expansion before planning",
        )
    
    statement = select(CharacterRecipe).join(
        Recipe,
        CharacterRecipe.recipe_id == Recipe.id,
    ).where(
        CharacterRecipe.character_id == character_id,
        Recipe.expansion_id == settings.current_expansion_id,
        Recipe.profession_id.in_([character.profession1_id, character.profession2_id]),
    )

    crs = session.exec(statement).all()

    if not crs:
        return []  # valid case: no recipes learned

    result = []

    for cr in crs:
        recipe = session.get(Recipe, cr.recipe_id)

        if not recipe:
            raise HTTPException(status_code=500, detail=f"Recipe {cr.recipe_id} missing")

        if cr.concentration_cost <= 0:
            raise HTTPException(status_code=400, detail="Invalid concentration cost")

        max_possible = character.concentration // cr.concentration_cost

        result.append({
            "recipe_id": recipe.id,
            "recipe_name": recipe.name,
            "profession_id": recipe.profession_id,
            "concentration_cost": cr.concentration_cost,
            "max_possible": max_possible
        })

    return result

@router.post("/")
def calculate_plan(plan: list[CharacterPlanItem], session: Session = Depends(get_session)):
    result = {}
    concentration_used = {}

    settings = session.get(AppSettings, 1)

    if settings is None:
        raise HTTPException(
            status_code=400,
            detail="Select an expansion before planning",
        )

    for item in plan:
        character = session.get(Character, item.character_id)

        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        # get concentration cost

        cr = session.exec(
            select(CharacterRecipe).where(
                CharacterRecipe.character_id == item.character_id,
                CharacterRecipe.recipe_id == item.recipe_id
            )
        ).first()

        if not cr:
            raise HTTPException(status_code=400, detail="Character does not know this recipe")

        cost = item.crafts * cr.concentration_cost

        recipe = session.get(Recipe, item.recipe_id)

        if recipe is None:
            raise HTTPException(
                status_code=404,
                detail="Recipe not found",
            )

        if recipe.profession_id not in (character.profession1_id, character.profession2_id):
            raise HTTPException(
                status_code=400,
                detail="Recipe does not belong to either active profession",
            )

        if recipe.expansion_id != settings.current_expansion_id:
            raise HTTPException(
                status_code=400,
                detail="Recipe does not belong to the selected expansion",
            )

        if cr.concentration_cost <= 0:
            raise HTTPException(
                status_code=400,
                detail="Invalid concentration cost",
            )

        budget_key = (item.character_id, recipe.profession_id)
        used = concentration_used.get(budget_key, 0)

        if used + cost > character.concentration:
            raise HTTPException(status_code=400, detail="Not enough concentration")

        concentration_used[budget_key] = used + cost

        # get recipe + ingredients

        recipe = session.exec(
            select(Recipe).options(
                selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient)
            ).where(Recipe.id == item.recipe_id)
        ).first()

        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

        for ri in recipe.ingredients:
            name = ri.ingredient.name
            total = ri.amount_required * item.crafts

            result[name] = result.get(name, 0) + total

    return result
