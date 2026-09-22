from fastapi import APIRouter, Depends
from ..dependencies import get_current_account, require_admin
from ..models import Account
from ..services.ingredients import IngredientService
from ..dtos import IngredientCreate, IngredientRead

ingredient_service = IngredientService()

router = APIRouter(
    prefix="/ingredients",
    tags=["ingredients"],
    dependencies=[Depends(get_current_account)],
)

@router.post('/', response_model=IngredientRead)
def create_ingredient(ingredient_data: IngredientCreate, account: Account = Depends(require_admin)):
    return ingredient_service.create_ingredient(ingredient_data)

@router.get('/', response_model=list[IngredientRead])
def get_ingredients(search: str | None = None):
    return ingredient_service.get_ingredients(search)
