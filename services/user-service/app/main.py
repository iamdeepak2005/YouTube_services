from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.middleware.cors import add_cors_middleware
from app.middleware.exception_handlers import add_exception_handlers
from app.routers.user_router import limiter, router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="User Service",
        description="Manages learner identities for the YouTube Learning Platform.",
        version="1.0.0",
        lifespan=lifespan,
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
        return {"service": "user-service", "status": "healthy"}

    return app


app = create_app()
