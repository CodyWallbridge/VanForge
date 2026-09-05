from fastapi import FastAPI
from contextlib import asynccontextmanager

from .seeds import seed_characters, seed_professions, seed_recipes
from .routers import characters, ingredients, recipes, planner

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    seed_professions()
    seed_characters()
    seed_recipes()
    yield
    # shutdown (nothing needed right now)

app = FastAPI(lifespan=lifespan)
    
app.include_router(characters.router)
app.include_router(ingredients.router)
app.include_router(recipes.router)
app.include_router(planner.router)

@app.get("/")
def root():
    return {"message": "VanForge API is running"}