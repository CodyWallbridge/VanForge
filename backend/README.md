# VanForge Backend

FastAPI and SQLModel API for managing characters, professions and expansion-specific crafting recipes.

## Setup

Run from the project root using your activated `.venv`:

```cmd
python -m pip install -r backend/requirements-dev.txt
python -m alembic upgrade head
```

For optional starter characters and Midnight recipes, explicitly run:

```cmd
python -m backend.app.seeds
```

The seed command can restore deleted starter entries or ingredient links. Normal startup only seeds the fixed profession catalog; it never restores characters or recipes. The initial migration creates Midnight and the selected-expansion setting. The explicit seed command creates missing initial settings without changing an existing selection.

## Run

From the project root:

```cmd
python -m uvicorn backend.app.main:app --reload
```

The VS Code Run Backend task also works. Interactive documentation: http://127.0.0.1:8000/docs

## Endpoints

| Resource | Operations |
| --- | --- |
| `/characters/` | Create and list |
| `/characters/{id}` | Read, PATCH name/professions/concentration, delete |
| `/characters/{id}/recipes` | List currently eligible assignments and assign a recipe |
| `/characters/{id}/recipes/{recipe_id}` | PATCH concentration cost or remove assignment |
| `/recipes/` | Create and list, optionally filtered by `expansion_id` and `profession_id` |
| `/recipes/{id}` | Read, PATCH details/ingredients, delete |
| `/recipes/{id}/profit` | PATCH profit in whole gold, including losses |
| `/recipes/{id}/calculate` | Calculate ingredients for a craft count |
| `/ingredients/` | List/search with `search`, create or reuse by name |
| `/professions/` | List fixed profession catalog |
| `/expansions/` | List and create |
| `/expansions/{id}` | Read, rename, delete |
| `/settings/` | Read or PATCH `current_expansion_id` |
| `/planner/options/{character_id}` | List eligible crafting options |
| `/planner/` | Validate a submitted plan and total its ingredients |

PATCH requests leave omitted fields unchanged and reject explicit null values. Supplying `ingredients` replaces the complete ingredient list; an empty list clears it.

Each recipe ingredient accepts either `ingredient_id` or `name`, plus positive `amount_required`. Names are trimmed and matched case-insensitively. Existing ingredients are reused. Referencing the same ingredient twice, even by ID and name, is rejected. Shared ingredients survive recipe deletion.

Characters have exactly two distinct professions and a concentration value from 0 to 1000. Each profession receives that full budget independently. Planning never spends the saved balance. Changing professions preserves learned recipes and costs; current lists and plans filter by active professions and selected expansion. Explicit assignment removal or character/recipe deletion removes the relevant learned-recipe rows.

Deleting a recipe also removes ingredient links. Expansion deletion is blocked while selected or while it contains recipes. Recipe edits, including ingredient creation and replacement, are committed together.

## Structure and database

- `app/models.py`: database tables and relationships.
- `app/dtos/`: request and response models.
- `app/routers/`: HTTP endpoints.
- `app/services/`: shared validation and ingredient resolution.
- `app/seeds.py`: fixed professions and explicitly invoked starter data.
- `backend/vanforge.db`: local SQLite database, ignored by Git.

Foreign keys are enabled on backend database connections. Alembic manages schema changes; see [the migration guide](../alembic/README). Missing records return 404, business validation returns 400, conflicts return 409, and request-schema validation returns 422. Successful deletion returns 204.

## Tests

From the project root:

```cmd
python -m pytest backend/tests/unit
```

The full integration suite is planned separately. Automatic profit optimization, recipe categories, and a dedicated ingredient-management screen are not implemented yet.
