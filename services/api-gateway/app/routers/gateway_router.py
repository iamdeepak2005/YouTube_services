from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.services.proxy_service import proxy_request

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.api_route("/users", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], tags=["Gateway → User"])
@router.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], tags=["Gateway → User"])
@limiter.limit("100/minute")
async def proxy_user_service(request: Request, path: str = ""):
    target_path = f"/{path}" if path else ""
    return await proxy_request(request, f"{settings.user_service_url}/users{target_path}", "user-service")


@router.api_route("/playlist", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], tags=["Gateway → Content"])
@router.api_route("/playlist/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], tags=["Gateway → Content"])
@limiter.limit("100/minute")
async def proxy_playlist(request: Request, path: str = ""):
    target_path = f"/{path}" if path else ""
    return await proxy_request(request, f"{settings.content_service_url}/playlist{target_path}", "content-service")


@router.api_route("/video", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], tags=["Gateway → Video"])
@router.api_route("/video/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], tags=["Gateway → Video"])
@limiter.limit("100/minute")
async def proxy_video(request: Request, path: str = ""):
    target_path = f"/{path}" if path else ""
    if path.startswith("progress") or path.startswith("resume"):
        return await proxy_request(request, f"{settings.progress_service_url}/video{target_path}", "progress-service")
    return await proxy_request(request, f"{settings.content_service_url}/video{target_path}", "content-service")


@router.api_route("/course", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], tags=["Gateway → Progress"])
@router.api_route("/course/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], tags=["Gateway → Progress"])
@limiter.limit("100/minute")
async def proxy_progress_service(request: Request, path: str = ""):
    target_path = f"/{path}" if path else ""
    return await proxy_request(request, f"{settings.progress_service_url}/course{target_path}", "progress-service")


@router.api_route("/analytics", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], tags=["Gateway → Analytics"])
@router.api_route("/analytics/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], tags=["Gateway → Analytics"])
@limiter.limit("100/minute")
async def proxy_analytics_service(request: Request, path: str = ""):
    target_path = f"/{path}" if path else ""
    return await proxy_request(request, f"{settings.analytics_service_url}/analytics{target_path}", "analytics-service")


@router.api_route("/recommend", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], tags=["Gateway → Recommendation"])
@router.api_route("/recommend/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], tags=["Gateway → Recommendation"])
@limiter.limit("100/minute")
async def proxy_recommendation_service(request: Request, path: str = ""):
    target_path = f"/{path}" if path else ""
    return await proxy_request(request, f"{settings.recommendation_service_url}/recommend{target_path}", "recommendation-service")
