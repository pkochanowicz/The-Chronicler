from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    await init_db()
    yield
    # Shutdown event
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "Welcome to The Chronicler API!"}

# TODO: Include routers for webhooks, health etc.
from routers import characters, health, webhooks, webhooks, health
app.include_router(characters.router, prefix="/characters", tags=["characters"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(health.router, prefix="/health", tags=["health"])