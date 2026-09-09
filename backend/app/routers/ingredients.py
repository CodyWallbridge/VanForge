from fastapi import APIRouter
from ..services.ingredients import IngredientService
from ..dtos import IngredientCreate, IngredientRead

ingredient_service = IngredientService()

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

@router.post('/', response_model=IngredientRead)
def create_ingredient(ingredient_data: IngredientCreate):
    return ingredient_service.create_ingredient(ingredient_data)

@router.get('/', response_model=list[IngredientRead])
def get_ingredients(search: str | None = None):
    return ingredient_service.get_ingredients(search)
