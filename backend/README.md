# VanForge Backend

FastAPI and SQLModel API for a WoW crafting planner.

The goal is to maximize recipe profit using each character’s
concentration amount as an independent budget for each profession.

## Setup

From the project root, install the backend dependencies:

```powershell
python -m pip install -r backend/requirements.txt
```

Create or update the database:

```powershell
python -m alembic upgrade head
```

## Run

From the project root:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs

Missing professions are seeded automatically at startup.

## Structure

- `app/main.py` — application setup and router registration.
- `app/database.py` — database connection and session handling.
- `app/models.py` — database tables and relationships.
- `app/dtos/` — API request and response models.
- `app/routers/` — API endpoints.
- `app/seeds.py` — initial profession data.
- `requirements.txt` — Python dependencies.

## Database

SQLite data is stored in `backend/vanforge.db`.
The database file is excluded from Git.

Foreign-key enforcement is enabled for backend connections.
Alembic manages table creation and schema changes.

Run migration commands from the project root. See
[the migration guide](../alembic/README) for instructions.

## Current status

The API supports creating and listing characters, ingredients,
and recipes, plus calculating ingredient requirements.

Recipes store profit per craft in whole gold.
Character recipes store character-specific concentration costs.

Automatic profit optimization and independent concentration
budgets per profession still need to be implemented in the planner.