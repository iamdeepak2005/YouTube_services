from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.middleware.cors import add_cors_middleware
from app.middleware.exception_handlers import add_exception_handlers
from app.routers.content_router import limiter, router
from app.services.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    scheduler = start_scheduler()
    yield
    scheduler.shutdown(wait=False)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Content Service",
        description="Manages YouTube playlist and video metadata with cache-first strategy.",
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
        return {"service": "content-service", "status": "healthy"}

    return app


app = create_app()
