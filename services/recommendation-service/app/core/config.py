from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    progress_service_url: str = "http://localhost:8003"
    content_service_url: str = "http://localhost:8002"
    analytics_service_url: str = "http://localhost:8004"
    service_port: int = 8005
    rate_limit_per_minute: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
