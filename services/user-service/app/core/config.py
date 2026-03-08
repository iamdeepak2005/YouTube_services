from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/user_db"
    service_port: int = 8001
    rate_limit_per_minute: int = 100
    page_size_default: int = 20
    page_size_max: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
