from fastapi import APIRouter, Response
from ..services.recipes import RecipeService
from ..dtos import RecipeCreate, RecipeRead, RecipeProfitUpdate, RecipeUpdate

recipe_service = RecipeService()

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.post('/', response_model=RecipeRead, status_code=201)
def create_recipe(recipe_data: RecipeCreate):
    return recipe_service.create_recipe(recipe_data)

@router.get('/', response_model=list[RecipeRead])
def get_recipes(expansion_id: int | None = None, profession_id: int | None = None):
    return recipe_service.get_recipes(expansion_id, profession_id)

@router.get('/{recipe_id}', response_model=RecipeRead)
def get_recipe(recipe_id: int):
    return recipe_service.get_recipe(recipe_id)

@router.patch('/{recipe_id}', response_model=RecipeRead)
def update_recipe(recipe_id: int, recipe_data: RecipeUpdate):
    return recipe_service.update_recipe(recipe_id, recipe_data)

@router.delete('/{recipe_id}', status_code=204)
def delete_recipe(recipe_id: int):
    recipe_service.delete_recipe(recipe_id)

    return Response(status_code=204)

@router.post('/{recipe_id}/calculate')
def calculate_recipe(recipe_id: int, crafts: int):
    return recipe_service.calculate_recipe(recipe_id, crafts)

@router.patch('/{recipe_id}/profit', response_model=RecipeRead)
def update_recipe_profit(recipe_id: int, profit_data: RecipeProfitUpdate):
    return recipe_service.update_recipe_profit(recipe_id, profit_data)
