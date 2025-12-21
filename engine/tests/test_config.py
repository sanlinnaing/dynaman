import os
from building_blocks.config import Settings

def test_settings_defaults():
    # Unset env vars to test defaults (safeguard)
    # In a real scenario, we might want to use mock.patch.dict(os.environ, clear=True)
    # But BaseSettings reads from env once on instantiation or via _env_file.
    
    # We can instantiate Settings directly to test defaults if no env vars interfere.
    settings = Settings(_env_file=None)
    assert settings.app_name == "Dyna Management Tool"
    assert settings.debug is False
    assert settings.mongodb_url == "mongodb://localhost:27017"

def test_settings_override():
    os.environ["APP_NAME"] = "Test App"
    os.environ["DEBUG"] = "True"
    
    try:
        settings = Settings(_env_file=None)
        assert settings.app_name == "Test App"
        assert settings.debug is True
    finally:
        del os.environ["APP_NAME"]
        del os.environ["DEBUG"]
