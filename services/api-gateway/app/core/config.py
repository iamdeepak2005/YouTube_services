from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    user_service_url: str = "http://localhost:8001"
    content_service_url: str = "http://localhost:8002"
    progress_service_url: str = "http://localhost:8003"
    analytics_service_url: str = "http://localhost:8004"
    recommendation_service_url: str = "http://localhost:8005"
    gateway_port: int = 8000
    rate_limit_per_minute: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
