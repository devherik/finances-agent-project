import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
else:
    print(f".env file not found at {ENV_PATH}, proceeding without it.")


class Settings(BaseSettings):
    debug_mode: bool = os.getenv("DEBUG_MODE", "True").lower() in ("true", "1", "yes")
    environment: str = os.getenv("ENVIRONMENT", "development")

    model_config = SettingsConfigDict(
        env_file=ENV_PATH, env_file_encoding="utf-8", extra="ignore"
    )

    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "your_password")
    postgres_user: str = os.getenv("POSTGRES_USER", "your_user")
    postgres_host: str = os.getenv("POSTGRES_HOST", "your_host")
    postgres_port: str = os.getenv("POSTGRES_PORT", "your_port")
    postgres_db: str = os.getenv("POSTGRES_DB", "your_db")

    # AI Model settings
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "your_gemini_api_key")
    gemini_project_id: str = os.getenv("GEMINI_PROJECT_ID", "your_gemini_project_id")
    gemini_standard_model_name: str = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    gemini_premium_model_name: str = os.getenv(
        "GEMINI_PREMIUM_MODEL_NAME", "gemini-2.5-premium"
    )
    gemini_pro_model_name: str = os.getenv(
        "GEMINI_PRO_MODEL_NAME", "gemini-3-pro-preview"
    )
    max_search_results: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))

    # Other settings
    log_level: str = "INFO"
    max_concurrent_requests: int = 5
    embedding_chunk_size: int = 384

    # Auth settings
    secret_key: str = os.getenv("SECRET_KEY", "your_secret_key")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    @property
    def is_dev(self) -> bool:
        return os.getenv("IS_DEV", "True").lower() in ("true", "1", "yes")

    @property
    def get_postgres_url(self) -> str:
        return f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def get_redis_url(self) -> str:
        return os.getenv("REDIS_URL", "redis://localhost:6379/0")

    @property
    def get_redis_index_name(self) -> str:
        return os.getenv("REDIS_INDEX_NAME", "knowledge")

    @property
    def get_async_postgres_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def get_supabase_connection_string(self) -> str:
        return f"postgresql://postgres:{self.postgres_password}@db.pzryulgwpfdxysottnqr.supabase.co:5432/postgres"


settings = Settings()
