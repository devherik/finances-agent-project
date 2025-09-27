import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '.env')

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
    print(f".env file loaded from {ENV_PATH}", "DEBUG")
else:
    print(f".env file not found at {ENV_PATH}, proceeding without it.", "WARNING")

class Settings(BaseSettings):
    debug_mode: bool = os.getenv("DEBUG_MODE", "True").lower() in ("true", "1", "yes")
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')

    mongodb_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongodb_database: str = os.getenv("MONGO_DATABASE", "test")
    mongodb_password: str = os.getenv("MONGO_PASSWORD", "your_password")

    # AI Model settings
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "your_gemini_api_key")
    gemini_standard_model_name: str = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    gemini_premium_model_name: str = os.getenv("GEMINI_PREMIUM_MODEL_NAME", "gemini-2.5-premium")
    max_search_results: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))

    # Other settings
    log_level: str = "INFO"
    max_concurrent_requests: int = 5
    
    @property
    def is_dev(self) -> bool:
        return os.getenv("IS_DEV", "True").lower() in ("true", "1", "yes")
    
    @property
    def get_mongo_connection_string(self) -> str:
        return f"mongodb+srv://herik:{self.mongodb_password}@cluster0.4tbavfq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

settings = Settings()