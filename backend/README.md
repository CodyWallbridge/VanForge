# VanForge Backend

FastAPI API for managing characters, professions, expansion-specific recipes, and crafting plans.

## Setup

Run these commands separately from the project root with your virtual environment activated:

```cmd
python -m pip install -r backend/requirements-dev.txt
python -m alembic upgrade head
```

To load starter characters and Midnight recipes:

```cmd
python -m backend.app.seeds
```

Normal startup seeds only the fixed profession catalog. The explicit seed command adds missing starter data and can restore deleted starter entries. It preserves an existing selected expansion.

## Running the backend

From the project root:

```cmd
python -m uvicorn backend.app.main:app --reload
```

You can also use the VS Code Run Backend task.

Interactive API documentation: http://127.0.0.1:8000/docs

## Structure

- `app/models.py`: SQLModel database tables and relationships.
- `app/dtos/`: Pydantic request and response models.
- `app/routers/`: HTTP endpoints and module-level service instances.
- `app/services/`: business rules and transaction ownership.
- `app/backend_models/`: CRUD classes and database queries.
- `app/utils/`: reusable validation utilities.
- `app/seeds.py`: profession catalog and optional starter data.
- `tests/unit/`: DTO and validation tests.
- `tests/integration/`: API, database, and transaction tests.

## Sessions and transactions

Routers call service wrapper methods without handling database sessions.

Wrappers such as `get_character`, `create_character`, and `delete_character` open a session using the service's configured engine. Write operations commit before returning. The session context manager closes the session and rolls back any uncommitted transaction on exit.

`BaseService` provides session-accepting methods including `get`, `get_all`, `create`, `update`, `delete`, and `delete_many`. Wrapper methods call these inherited methods using their active session.

When a service calls another service within a transaction, it passes the same session. The receiving method uses that session without committing or closing it.

CRUD instances are configured with a table model and receive a session for each operation. CRUD methods do not commit. The CRUD `delete_many` method rolls back the supplied session if a deletion fails.

Generic base methods do not automatically apply the business checks in wrapper methods. For example, expansion deletion restrictions are enforced by `delete_expansion`, not by generic bulk deletion. No bulk deletion endpoints are exposed.

Services accept `engine_override` for isolated integration tests. Shared service instances do not store active sessions.

Responses are refreshed, loaded with required relationships, or converted to DTOs before their sessions close.

## Database and migrations

The application uses SQLite at `backend/vanforge.db`. This file is ignored by Git.

Foreign-key enforcement is enabled on application database connections. Alembic manages schema changes.

After changing table definitions:

```cmd
python -m alembic revision --autogenerate -m "Describe the schema change"
```

Review the generated migration, then apply it:

```cmd
python -m alembic upgrade head
```

Character-recipe and recipe-ingredient links have individual ID primary keys and unique constraints on their associated pairs.

Deleting a character removes its recipe assignments. Deleting a recipe removes its assignments and ingredient links. Shared ingredients remain.

## Endpoints

| Resource | Operations |
| --- | --- |
| `/characters/` | Create and list |
| `/characters/{id}` | Read, update, delete |
| `/characters/{id}/recipes` | List current assignments and assign recipes |
| `/characters/{id}/recipes/{recipe_id}` | Update concentration cost or remove assignment |
| `/recipes/` | Create and list; optional expansion and profession filters |
| `/recipes/{id}` | Read, update, delete |
| `/recipes/{id}/profit` | Update profit in whole gold |
| `/recipes/{id}/calculate` | Calculate ingredients for a craft count |
| `/ingredients/` | Search/list and create or reuse ingredients |
| `/professions/` | List professions |
| `/expansions/` | Create and list |
| `/expansions/{id}` | Read, rename, delete |
| `/settings/` | Read or change the selected expansion |
| `/planner/options/{character_id}` | List eligible crafting options |
| `/planner/` | Validate a submitted plan and total ingredients |
| `/planner/optimize` | Maximize profit for selected characters |

## Crafting rules

Characters have two distinct professions and a concentration balance from 0 to 1000. Each profession independently receives the character's full concentration budget. Planning does not spend the saved balance.

Changing professions preserves learned recipes and concentration costs. Current recipe lists and planning use active professions and the selected expansion.

Recipes store profit in whole gold, including negative values. Concentration costs belong to character-recipe assignments.

Recipe ingredients accept either an ingredient ID or a name, together with a positive quantity. Existing names are intended to match case-insensitively. Duplicate ingredients within a recipe are rejected.

PATCH requests preserve omitted fields and reject explicit null values. Supplying an ingredient list replaces all recipe ingredients; an empty list clears them.

An expansion cannot be deleted while selected or while it contains recipes. Recipe updates and their ingredient changes are committed together.

Recipe categories and frontend craft-list export/import are not implemented yet.

## Tests

Run all tests:

```cmd
python -m pytest
```

Run either group separately:

```cmd
python -m pytest backend/tests/unit
python -m pytest backend/tests/integration
```

Integration tests use an isolated in-memory SQLite database with foreign keys enabled. Router service instances receive the test engine, and startup seeding is redirected to the test database.
## Profit optimization

POST `/planner/optimize` with a nonempty list of unique character IDs:

```json
{"character_ids": [1, 2, 3]}
```

The response contains `expansion_id`, `total_profit` in whole gold, a combined
`crafts` list, and a `characters` breakdown. Each character includes profit and
per-profession concentration used, concentration remaining, and profit.

The exact optimizer evaluates whole-number combinations with unlimited repeats.
It considers only known recipes in active professions and the selected expansion.
Each profession independently receives the character's full saved concentration.
Profit means entered net profit per craft; ingredient costs are not subtracted again.
Equal-profit plans prefer less concentration. Zero-profit and loss-making crafts
are omitted, and characters without profitable options remain in the breakdown.
No saved concentration or recipe data is changed.

Submit the response's `crafts` array directly to POST `/planner/` to calculate
materials, optionally adjusting quantities first. The manual planner revalidates
against current settings, professions, and concentration. There are no inventory
or sales caps. Select-all clients send all selected character IDs in the same request.
