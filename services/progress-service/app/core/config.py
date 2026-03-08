from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/progress_db"
    content_service_url: str = "http://localhost:8002"
    service_port: int = 8003
    rate_limit_per_minute: int = 100
    completion_threshold: float = 0.90
    page_size_default: int = 20
    page_size_max: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
