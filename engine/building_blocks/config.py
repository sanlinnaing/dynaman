from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "dynaman"
    
    # App Configuration
    app_name: str = "Dyna Management Tool"
    debug: bool = False
    MAX_RECORDS_PER_PAGE: int = 50

    # Tell Pydantic to read from a .env file
    model_config = SettingsConfigDict(env_file=".env")

# Global settings instance
settings = Settings()