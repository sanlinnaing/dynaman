from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router_auth import router as auth_router
from api.v1.router_groups import router as groups_router
from contextlib import asynccontextmanager
from api.dependencies import get_user_repository, get_db
from domain.entities.user import User, UserRole
from domain.services.security_service import SecurityService
from opentelemetry_config import setup_opentelemetry

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed default admin
    db = await get_db()
    user_repo = await get_user_repository(db)
    
    admin_email = "admin@dynaman.com"
    existing_admin = await user_repo.get_by_email(admin_email)
    
    if not existing_admin:
        print(f"Seeding default admin: {admin_email}")
        hashed_password = SecurityService.get_password_hash("admin")
        admin_user = User(
            email=admin_email,
            hashed_password=hashed_password,
            role=UserRole.SYSTEM_ADMIN
        )
        await user_repo.create(admin_user)
    else:
        print("Default admin already exists.")
        
    yield
    # Shutdown logic (if any)

app = FastAPI(title="Dynaman Auth Service", lifespan=lifespan)

# Setup OpenTelemetry
setup_opentelemetry(app)

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

# New Relic UI Config Endpoint
import os
from pydantic import BaseModel

class UiTelemetryConfig(BaseModel):
    new_relic_browser_ingest_key: str
    new_relic_browser_app_id: str
    environment: str

@app.get("/api/v1/config/ui", response_model=UiTelemetryConfig)
async def ui_config():
    return UiTelemetryConfig(
        new_relic_browser_ingest_key=os.environ.get("NEW_RELIC_BROWSER_INGEST_KEY", ""),
        new_relic_browser_app_id=os.environ.get("NEW_RELIC_BROWSER_APP_ID", ""),
        environment=os.environ.get("APP_ENVIRONMENT", "unknown"),
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(groups_router, prefix="/api/v1/groups", tags=["groups"])
