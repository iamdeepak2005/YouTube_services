from typing import Tuple
import asyncio

import httpx
from fastapi import FastAPI

from app.core.config import settings
from app.middleware.cors import add_cors_middleware
from app.middleware.exception_handlers import add_exception_handlers
from app.routers.gateway_router import limiter, router

SERVICE_HEALTH_URLS = {
    "user-service": f"{settings.user_service_url}/health",
    "content-service": f"{settings.content_service_url}/health",
    "progress-service": f"{settings.progress_service_url}/health",
    "analytics-service": f"{settings.analytics_service_url}/health",
    "recommendation-service": f"{settings.recommendation_service_url}/health",
}


def create_app() -> FastAPI:
    app = FastAPI(
        title="YouTube Learning Platform — API Gateway",
        description="Unified reverse proxy for all microservices.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        redirect_slashes=False,
    )

    add_cors_middleware(app)
    app.state.limiter = limiter
    add_exception_handlers(app, limiter)
    app.include_router(router)

    @app.get("/health", tags=["Health"])
    async def health():
        results = {"gateway": "healthy", "services": {}}

        async def check(name: str, url: str) -> Tuple[str, str]:
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    resp = await client.get(url)
                    return name, "healthy" if resp.status_code == 200 else "degraded"
            except Exception:
                return name, "unreachable"

        checks = await asyncio.gather(*[check(n, u) for n, u in SERVICE_HEALTH_URLS.items()])
        results["services"] = dict(checks)
        return results

    @app.get("/", tags=["Gateway"])
    def service_map():
        return {
            "gateway": "YouTube Learning Platform API Gateway",
            "version": "1.0.0",
            "routes": {
                "/users/*": "user-service",
                "/playlist/*": "content-service",
                "/video/*": "content-service | progress-service",
                "/course/*": "progress-service",
                "/analytics/*": "analytics-service",
                "/recommend/*": "recommendation-service",
            },
        }

    return app


app = create_app()
