import pytest
from fastapi import HTTPException
from sqlmodel import Session
from backend.app.dtos import ExpansionCreate
from backend.app.models import Expansion
from backend.app.services.expansions import ExpansionService

def test_inherited_get_and_get_all_use_supplied_session(test_engine):
    service = ExpansionService(engine_override=test_engine)

    with Session(test_engine) as session:
        expansion = Expansion(name="Test Expansion")
        service.create(entity=expansion, session=session)

        assert service.get(session, expansion.id) is expansion
        assert service.get_all(session) == [expansion]
        assert service.get(session, 99999) is None

        session.rollback()

    with Session(test_engine) as session:
        assert service.get_all(session) == []

@pytest.mark.parametrize("blocked_by", ["selected", "recipes"])
def test_delete_wrapper_preserves_restricted_expansions(
    test_engine,
    catalog,
    blocked_by,
):
    service = ExpansionService(engine_override=test_engine)
    blocked_id = catalog["midnight"] if blocked_by == "selected" else catalog["future"]

    with pytest.raises(HTTPException) as error:
        service.delete_expansion(blocked_id)

    assert error.value.status_code == 409
    assert service.get_expansion(blocked_id).id == blocked_id

def test_delete_wrapper_reports_missing_record(test_engine):
    service = ExpansionService(engine_override=test_engine)

    with pytest.raises(HTTPException) as error:
        service.delete_expansion(99999)

    assert error.value.status_code == 404

@pytest.mark.parametrize("count, remaining", [(1, ["Second"]), (-1, []), (0, ["First", "Second"])])
def test_bulk_delete_respects_count_and_caller_transaction(
    test_engine,
    count,
    remaining,
):
    service = ExpansionService(engine_override=test_engine)
    first_data = ExpansionCreate(name="First")
    second_data = ExpansionCreate(name="Second")
    service.create_expansion(first_data)
    service.create_expansion(second_data)

    with Session(test_engine) as session:
        instances = service.get_all(session)
        result = service.delete_many(
            session,
            instances,
            count,
        )

        assert result is True
        assert [item.name for item in service.get_all(session)] == remaining

        session.rollback()

    assert len(service.get_expansions()) == 2

def test_bulk_delete_empty_input_returns_false(test_engine):
    service = ExpansionService(engine_override=test_engine)

    with Session(test_engine) as session:
        result = service.delete_many(
            session,
            [],
            -1,
        )

        assert result is False
