from unittest.mock import Mock
import pytest
from fastapi import HTTPException
from sqlmodel import Session, select
from backend.app.dtos import ExpansionCreate, RecipeCreate, RecipeUpdate, RecipeIngredientCreate
from backend.app.models import Expansion, Ingredient, Recipe
from backend.app.services import expansions
from backend.app.services.expansions import ExpansionService
from backend.app.services.recipe_ingredients import RecipeIngredientService
from backend.app.services.recipes import RecipeService

def test_inherited_create_does_not_commit_or_close_session(test_engine, monkeypatch):
    service = ExpansionService(engine_override=test_engine)

    with Session(test_engine) as session:
        commit = Mock(wraps=session.commit)
        rollback = Mock(wraps=session.rollback)
        close = Mock(wraps=session.close)
        monkeypatch.setattr(
            session,
            "commit",
            commit,
        )
        monkeypatch.setattr(
            session,
            "rollback",
            rollback,
        )
        monkeypatch.setattr(
            session,
            "close",
            close,
        )
        expansion = Expansion(name="Caller Owned")
        service.create(entity=expansion, session=session)
        expansion_id = expansion.id

        assert service.get(session, expansion_id).name == "Caller Owned"
        commit.assert_not_called()
        rollback.assert_not_called()
        close.assert_not_called()

        session.rollback()

    with Session(test_engine) as session:
        assert session.get(Expansion, expansion_id) is None

def test_nested_validation_error_leaves_caller_transaction_open(test_engine):
    service = RecipeIngredientService()

    with Session(test_engine) as session:
        pending = Ingredient(name="Pending")
        session.add(pending)
        session.flush()
        entry = RecipeIngredientCreate(ingredient_id=99999, amount_required=1)

        with pytest.raises(HTTPException) as error:
            service.resolve_ingredients([entry], session=session)

        assert error.value.status_code == 404
        assert session.get(Ingredient, pending.id) is pending

        session.commit()

    with Session(test_engine) as session:
        assert session.exec(select(Ingredient)).one().name == "Pending"

def test_wrappers_open_separate_sessions_and_only_writes_commit(test_engine, monkeypatch):
    sessions = []
    commits = []
    closes = []

    def make_session(*args, **kwargs):
        session = Session(*args, **kwargs)
        commit = Mock(wraps=session.commit)
        close = Mock(wraps=session.close)
        session.commit = commit
        session.close = close
        sessions.append(session)
        commits.append(commit)
        closes.append(close)
        return session

    monkeypatch.setattr(
        expansions,
        "Session",
        make_session,
    )
    service = ExpansionService(engine_override=test_engine)
    data = ExpansionCreate(name="Reusable Service")
    expansion = service.create_expansion(data)
    result = service.get_expansion(expansion.id)

    assert result.name == "Reusable Service"
    assert len(sessions) == 2
    assert sessions[0] is not sessions[1]
    assert "session" not in vars(service)
    commits[0].assert_called_once()
    commits[1].assert_not_called()

    for close in closes:
        close.assert_called_once()

def test_nested_link_creation_is_rolled_back_by_owner(test_engine, catalog):
    service = RecipeIngredientService()
    entry = RecipeIngredientCreate(name="Nested Herb", amount_required=2)

    with pytest.raises(RuntimeError, match="abort outer operation"):
        with Session(test_engine) as session:
            recipe = Recipe(
                name="Nested Recipe",
                profession_id=catalog["alchemy"],
                expansion_id=catalog["midnight"],
            )
            session.add(recipe)
            session.flush()
            resolved = service.resolve_ingredients([entry], session=session)
            service.add_ingredient_links(
                recipe.id,
                resolved,
                session=session,
            )
            raise RuntimeError("abort outer operation")

    with Session(test_engine) as session:
        recipe_query = select(Recipe).where(Recipe.name == "Nested Recipe")
        ingredient_query = select(Ingredient).where(Ingredient.name == "Nested Herb")

        assert session.exec(recipe_query).all() == []
        assert session.exec(ingredient_query).all() == []

def test_recipe_wrappers_return_current_relationships_after_session_closes(test_engine, catalog):
    service = RecipeService(engine_override=test_engine)
    entry = RecipeIngredientCreate(name="Shared Herb", amount_required=2)
    data = RecipeCreate(
        name="Updated Recipe",
        profession_id=catalog["alchemy"],
        expansion_id=catalog["midnight"],
        ingredients=[entry],
    )
    recipe = service.create_recipe(data)
    recipe_id = recipe.id

    assert recipe.ingredients[0].amount_required == 2
    assert recipe.ingredients[0].ingredient.name == "Shared Herb"

    replacement = RecipeIngredientCreate(name="Shared Herb", amount_required=5)
    changes = RecipeUpdate(ingredients=[replacement])
    updated = service.update_recipe(recipe_id, changes)

    assert updated.ingredients[0].amount_required == 5
    assert updated.ingredients[0].ingredient.name == "Shared Herb"
    assert service.get_recipe(recipe_id).ingredients[0].amount_required == 5
