from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router_auth import router as auth_router
from contextlib import asynccontextmanager
from api.dependencies import get_user_repository, get_db
from domain.entities.user import User, UserRole
from domain.services.security_service import SecurityService

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

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
