from fastapi import FastAPI
from contextlib import asynccontextmanager

from .seeds import seed_professions
from .routers import characters, ingredients, recipes, planner, expansions, settings, professions

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    seed_professions()
    yield
    # shutdown (nothing needed right now)

app = FastAPI(lifespan=lifespan)
    
app.include_router(characters.router)
app.include_router(ingredients.router)
app.include_router(recipes.router)
app.include_router(planner.router)
app.include_router(expansions.router)
app.include_router(settings.router)
app.include_router(professions.router)

@app.get("/")
def root():
    return {"message": "VanForge API is running"}