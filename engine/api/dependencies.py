from motor.motor_asyncio import AsyncIOMotorClient
from building_blocks.config import settings
from metadata_context.infrastructure.schema_repository import SchemaRepository
from execution_context.infrastructure.record_repository import RecordRepository
from execution_context.application.record_use_cases import RecordUseCase
from metadata_context.application.schema_use_cases import SchemaApplicationService

# Initialize variables to None
client = None
db = None

def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]

def disconnect_db():
    global client
    if client:
        client.close()

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