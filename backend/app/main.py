import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from .utils.validation import InvalidNameError
from .seeds import seed_professions
from .routers import accounts, characters, ingredients, recipes, planner, expansions, settings, professions

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    seed_professions()
    yield
    # shutdown (nothing needed right now)

app = FastAPI(lifespan=lifespan)

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router)
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

@app.exception_handler(InvalidNameError)
async def handle_invalid_name(request: Request, error: InvalidNameError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(error)},
    )

@app.exception_handler(IntegrityError)
async def handle_integrity_error(request: Request, error: IntegrityError):
    return JSONResponse(status_code=409, content={"detail": "Change conflicts with existing data"})
