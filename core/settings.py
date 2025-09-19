import os
from typing import Optional
from dotenv import load_dotenv
from helpers.loging_helper import log_message
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '..', '.env')

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
    log_message(f".env file loaded from {ENV_PATH}", "DEBUG")
else:
    log_message(f".env file not found at {ENV_PATH}, proceeding without it.", "WARNING")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')

    mongodb_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongodb_database: str = os.getenv("MONGO_DATABASE", "test")

    # AI Model settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "your_openai_api_key")
    openai_model_name: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4")
    openai_max_retries: int = 3

    # Embedding settings
    embedding_model_name: str = "text-embedding-ada-002"

    # Other settings
    log_level: str = "INFO"
    max_concurrent_requests: int = 5

    """@property
    def sqlserver_connection_string(self) -> str:
        user = quote_plus(self.sqlserver_user)
        password = quote_plus(self.sqlserver_password)
        host = self.sqlserver_host
        port = self.sqlserver_port
        database = self.sqlserver_database
        return f"mssql+pyodbc://{user}:{password}@{host}:{port}/{database}?driver=ODBC+Driver+17+for+SQL+Server"""

settings = Settings()