from fastapi import APIRouter, Response
from ..services.expansions import ExpansionService
from ..dtos import ExpansionCreate, ExpansionRead, ExpansionUpdate

expansion_service = ExpansionService()

router = APIRouter(prefix="/expansions", tags=["expansions"])

@router.get('/', response_model=list[ExpansionRead])
def get_expansions():
    return expansion_service.get_expansions()

@router.get('/{expansion_id}', response_model=ExpansionRead)
def get_expansion(expansion_id: int):
    return expansion_service.get_expansion(expansion_id)

@router.post('/', response_model=ExpansionRead, status_code=201)
def create_expansion(expansion_data: ExpansionCreate):
    return expansion_service.create_expansion(expansion_data)

@router.patch('/{expansion_id}', response_model=ExpansionRead)
def update_expansion(expansion_id: int, expansion_data: ExpansionUpdate):
    return expansion_service.update_expansion(expansion_id, expansion_data)

@router.delete('/{expansion_id}', status_code=204)
def delete_expansion(expansion_id: int):
    expansion_service.delete_expansion(expansion_id)

    return Response(status_code=204)
