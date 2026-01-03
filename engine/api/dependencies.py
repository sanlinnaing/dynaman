from motor.motor_asyncio import AsyncIOMotorClient
from building_blocks.config import settings
from metadata_context.infrastructure.schema_repository import SchemaRepository
from execution_context.infrastructure.record_repository import RecordRepository
from execution_context.application.record_use_cases import RecordUseCase
from metadata_context.application.schema_use_cases import SchemaApplicationService
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

# Initialize variables to None
client = None
db = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]

def disconnect_db():
    global client
    if client:
        client.close()

async def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        role: str = payload.get("role", "user") # Default to user if role not present
        if email is None:
            raise credentials_exception
        return {"email": email, "role": role}
    except JWTError:
        raise credentials_exception

async def require_system_admin(current_user: dict = Depends(verify_token)):
    if current_user["role"] != "system_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires System Admin privileges"
        )
    return current_user

def get_record_use_case() -> RecordUseCase:
    global db
    if db is None:
        connect_db()
        
    # Infrastructure
    schema_repo = SchemaRepository(db)
    record_repo = RecordRepository(db)
    
    # Application Service
    return RecordUseCase(record_repo, schema_repo)

def get_schema_service() -> SchemaApplicationService:
    global db
    if db is None:
        connect_db()

    repo = SchemaRepository(db)
    return SchemaApplicationService(repo)