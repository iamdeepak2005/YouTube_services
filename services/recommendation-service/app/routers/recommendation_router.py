from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.controllers.recommendation_controller import RecommendationController

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=["Recommendations"])


@router.get("/recommend/{playlist_id}")
@limiter.limit("100/minute")
def get_recommendation(request: Request, playlist_id: str, user_id: str):
    return RecommendationController.get_recommendation(playlist_id, user_id)
