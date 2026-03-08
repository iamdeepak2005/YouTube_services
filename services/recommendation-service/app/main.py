from fastapi import FastAPI

from app.middleware.cors import add_cors_middleware
from app.middleware.exception_handlers import add_exception_handlers
from app.routers.recommendation_router import limiter, router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Recommendation Service",
        description="Computes video recommendations: resume → next-in-sequence → popular.",
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
    def health():
        return {"service": "recommendation-service", "status": "healthy"}

    return app


app = create_app()
