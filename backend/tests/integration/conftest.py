import pytest
from fastapi.testclient import TestClient
import os
from sqlalchemy.engine import make_url
from sqlmodel import SQLModel, Session, create_engine, select
from backend.app import database, main, seeds
from backend.app.dependencies import get_current_account
from backend.app.models import Account, AppSettings, Expansion, Profession, Recipe
from backend.app.routers import accounts, characters, expansions, ingredients, planner, professions, recipes, settings
from backend.app.services.accounts import AccountService
from backend.app.services.characters import CharacterService
from backend.app.services.expansions import ExpansionService
from backend.app.services.ingredients import IngredientService
from backend.app.services.planner import PlannerService
from backend.app.services.professions import ProfessionService
from backend.app.services.recipes import RecipeService
from backend.app.services.settings import SettingsService

@pytest.fixture
def test_engine(
    monkeypatch,
):
    test_database_url = os.getenv("TEST_DATABASE_URL")

    if not test_database_url:
        raise RuntimeError("TEST_DATABASE_URL is not set")

    test_database_url = make_url(test_database_url).set(drivername="postgresql+psycopg")

    if test_database_url == database.DATABASE_URL:
        raise RuntimeError("TEST_DATABASE_URL must not use the development database")

    engine = create_engine(test_database_url, pool_pre_ping=True)

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    monkeypatch.setattr(
        database,
        "engine",
        engine,
    )
    monkeypatch.setattr(
        seeds,
        "engine",
        engine,
    )

    try:
        yield engine
    finally:
        SQLModel.metadata.drop_all(engine)
        engine.dispose()

@pytest.fixture
def catalog(
    test_engine,
):
    seeds.seed_professions()

    with Session(test_engine) as session:
        professions = session.exec(
            select(Profession),
        ).all()
        profession_ids = {profession.name: profession.id for profession in professions}
        account = Account(
            auth_user_id="integration-test-user",
            email="integration@example.com",
            role="admin",
        )
        midnight = Expansion(name="Midnight")
        future = Expansion(name="Future")
        session.add(account)
        session.add(midnight)
        session.add(future)
        session.flush()

        settings = AppSettings(account_id=account.id, current_expansion_id=midnight.id)
        flask = Recipe(
            name="Flask",
            profession_id=profession_ids["Alchemy"],
            expansion_id=midnight.id,
        )
        alloy = Recipe(
            name="Alloy",
            profession_id=profession_ids["Blacksmithing"],
            expansion_id=midnight.id,
        )
        future_flask = Recipe(
            name="Future Flask",
            profession_id=profession_ids["Alchemy"],
            expansion_id=future.id,
        )
        session.add_all([settings, flask, alloy, future_flask])
        session.commit()

        return {
            "account": account.id,
            "alchemy": profession_ids["Alchemy"],
            "tailoring": profession_ids["Tailoring"],
            "blacksmithing": profession_ids["Blacksmithing"],
            "midnight": midnight.id,
            "future": future.id,
            "flask": flask.id,
            "alloy": alloy.id,
            "future_flask": future_flask.id,
        }

@pytest.fixture
def client(
    test_engine,
    catalog,
    monkeypatch,
):
    # Replace module-level services, not sessions, using the public engine override.
    monkeypatch.setattr(
        accounts,
        "account_service",
        AccountService(engine_override=test_engine),
    )
    monkeypatch.setattr(
        characters,
        "character_service",
        CharacterService(engine_override=test_engine),
    )
    monkeypatch.setattr(
        expansions,
        "expansion_service",
        ExpansionService(engine_override=test_engine),
    )
    monkeypatch.setattr(
        ingredients,
        "ingredient_service",
        IngredientService(engine_override=test_engine),
    )
    monkeypatch.setattr(
        planner,
        "planner_service",
        PlannerService(engine_override=test_engine),
    )
    monkeypatch.setattr(
        professions,
        "profession_service",
        ProfessionService(engine_override=test_engine),
    )
    monkeypatch.setattr(
        recipes,
        "recipe_service",
        RecipeService(engine_override=test_engine),
    )
    monkeypatch.setattr(
        settings,
        "settings_service",
        SettingsService(engine_override=test_engine),
    )

    def override_current_account():
        with Session(test_engine) as session:
            return session.get(Account, catalog["account"])

    main.app.dependency_overrides[get_current_account] = override_current_account

    try:
        with TestClient(main.app) as test_client:
            yield test_client
    finally:
        main.app.dependency_overrides.pop(get_current_account, None)

@pytest.fixture
def character(
    client,
    catalog,
):
    response = client.post("/characters/", json={"name": "Tester", "profession1_id": catalog["alchemy"], "profession2_id": catalog["tailoring"]})
    assert response.status_code == 201, response.text

    return response.json()
