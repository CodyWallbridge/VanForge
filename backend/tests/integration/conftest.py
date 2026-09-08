import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select
from backend.app import database, main, seeds
from backend.app.models import AppSettings, Expansion, Profession, Recipe

@pytest.fixture
def test_engine(
    monkeypatch,
):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(
        connection,
        connection_record,
    ):
        connection.execute("PRAGMA foreign_keys=ON")

    # Redirect both request sessions and startup seeding away from the saved DB.
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(seeds, "engine", engine)
    SQLModel.metadata.create_all(engine)

    try:
        yield engine
    finally:
        engine.dispose()

@pytest.fixture
def catalog(
    test_engine,
):
    seeds.seed_professions()

    with Session(test_engine) as session:
        professions = session.exec(select(Profession)).all()
        profession_ids = {profession.name: profession.id for profession in professions}
        midnight = Expansion(name="Midnight")
        future = Expansion(name="Future")
        session.add(midnight)
        session.add(future)
        session.flush()

        settings = AppSettings(id=1, current_expansion_id=midnight.id)
        flask = Recipe(name="Flask", profession_id=profession_ids["Alchemy"], expansion_id=midnight.id)
        alloy = Recipe(name="Alloy", profession_id=profession_ids["Blacksmithing"], expansion_id=midnight.id)
        future_flask = Recipe(name="Future Flask", profession_id=profession_ids["Alchemy"], expansion_id=future.id)
        session.add_all([settings, flask, alloy, future_flask])
        session.commit()

        return {
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
):
    def get_test_session():
        with Session(test_engine) as session:
            yield session

    previous_overrides = main.app.dependency_overrides.copy()
    main.app.dependency_overrides[database.get_session] = get_test_session

    try:
        # Run the real lifespan, including profession seeding on the test engine.
        with TestClient(main.app) as test_client:
            yield test_client
    finally:
        main.app.dependency_overrides.clear()
        main.app.dependency_overrides.update(previous_overrides)

@pytest.fixture
def character(
    client,
    catalog,
):
    response = client.post(
        "/characters/",
        json={"name": "Tester", "profession1_id": catalog["alchemy"], "profession2_id": catalog["tailoring"]},
    )
    assert response.status_code == 201, response.text

    return response.json()
