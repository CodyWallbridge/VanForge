from fastapi import APIRouter, Depends, Response
from ..dependencies import get_current_account
from ..services.characters import CharacterService
from ..dtos import CharacterCreate, CharacterRead, CharacterUpdate
from ..dtos import CharacterRecipeCreate, CharacterRecipeRead, CharacterRecipeUpdate
from ..models import Account

character_service = CharacterService()

router = APIRouter(prefix="/characters", tags=["characters"])

@router.post('/', response_model=CharacterRead, status_code=201)
def create_character(character_data: CharacterCreate, account: Account = Depends(get_current_account)):
    return character_service.create_character(character_data, account.id)

@router.get('/', response_model=list[CharacterRead])
def get_characters(account: Account = Depends(get_current_account)):
    return character_service.get_characters(account.id)

@router.get('/{character_id}', response_model=CharacterRead)
def get_character(character_id: int, account: Account = Depends(get_current_account)):
    return character_service.get_character(character_id, account.id)

@router.patch('/{character_id}', response_model=CharacterRead)
def update_character(character_id: int, character_data: CharacterUpdate, account: Account = Depends(get_current_account)):
    return character_service.update_character(character_id, character_data, account.id)

@router.delete('/{character_id}', status_code=204)
def delete_character(character_id: int, account: Account = Depends(get_current_account)):
    character_service.delete_character(character_id, account.id)

    return Response(status_code=204)

@router.get('/{character_id}/recipes', response_model=list[CharacterRecipeRead])
def get_character_recipes(character_id: int, account: Account = Depends(get_current_account)):
    return character_service.get_character_recipes(character_id, account.id)

@router.post('/{character_id}/recipes', response_model=CharacterRecipeRead, status_code=201)
def assign_recipe(character_id: int, recipe_data: CharacterRecipeCreate, account: Account = Depends(get_current_account)):
    return character_service.assign_recipe(character_id, recipe_data, account.id)

@router.patch('/{character_id}/recipes/{recipe_id}', response_model=CharacterRecipeRead)
def update_character_recipe(character_id: int, recipe_id: int, recipe_data: CharacterRecipeUpdate, account: Account = Depends(get_current_account)):
    return character_service.update_character_recipe(
        character_id,
        recipe_id,
        recipe_data,
        account.id,
    )

@router.delete('/{character_id}/recipes/{recipe_id}', status_code=204)
def remove_character_recipe(character_id: int, recipe_id: int, account: Account = Depends(get_current_account)):
    character_service.remove_character_recipe(character_id, recipe_id, account.id)

    return Response(status_code=204)
