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

app = FastAPI(title=f"Dyna Management Tool - {settings.app_mode.capitalize()}", lifespan=lifespan)

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