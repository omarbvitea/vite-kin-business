from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from sqlmodel import SQLModel
from app.db.session import engine

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
def on_startup():
    # In production, use Alembic migrations
    # However, for a ready-to-run app, we can also ensure tables exist
    SQLModel.metadata.create_all(engine)

@app.get("/")
def root():
    return {"message": "Welcome to Family Tree API"}
