import os
from unittest import mock
from building_blocks.config import Settings

def test_settings_defaults():
    # Remove MONGODB_URL from env if present to test defaults
    with mock.patch.dict(os.environ, {}, clear=True):
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
