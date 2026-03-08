from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/content_db"
    youtube_api_key: str = ""
    service_port: int = 8002
    rate_limit_per_minute: int = 100
    cache_ttl_hours: int = 24
    page_size_default: int = 20
    page_size_max: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
