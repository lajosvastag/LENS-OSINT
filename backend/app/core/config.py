from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "LENS OSINT Asset Intelligence Platform"
    app_env: str = "development"
    secret_key: str = "change-me-in-production"
    database_url: str = "sqlite:///./lens.db"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:3000"
    demo_mode: bool = True
    request_timeout_seconds: float = 5.0
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
