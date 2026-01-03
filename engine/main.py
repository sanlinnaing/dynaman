import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.v1.router_metadata import router as metadata_router
from api.v1.router_execution import router as execution_router
from building_blocks.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    from api.dependencies import connect_db, disconnect_db, db
    connect_db()
    # Need to re-import db or access it via module after connect_db
    import api.dependencies
    
    from execution_context.infrastructure.record_repository import RecordRepository
    repo = RecordRepository(api.dependencies.db)
    await repo.init_indices()
    yield
    # on shutdown
    disconnect_db()

# Include Versioned Routers based on APP_MODE
docs_url = "/api/v1/docs"
openapi_url = "/api/v1/openapi.json"

if settings.app_mode == "metadata":
    docs_url = "/api/v1/schemas/docs"
    openapi_url = "/api/v1/schemas/openapi.json"
elif settings.app_mode == "execution":
    docs_url = "/api/v1/data/docs"
    openapi_url = "/api/v1/data/openapi.json"

app = FastAPI(
    title=f"Dyna Management Tool - {settings.app_mode.capitalize()}",
    lifespan=lifespan,
    docs_url=docs_url,
    openapi_url=openapi_url
)

# CORS Configuration
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",  # React default
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Versioned Routers based on APP_MODE
if settings.app_mode in ["all", "metadata"]:
    app.include_router(metadata_router)

if settings.app_mode in ["all", "execution"]:
    app.include_router(execution_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)