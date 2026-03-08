from fastapi import HTTPException, status

from app.services.recommendation_engine import build_recommendation


class RecommendationController:

    @staticmethod
    def get_recommendation(playlist_id: str, user_id: str):
        result = build_recommendation(playlist_id, user_id)
        if result.get("reason") == "playlist_not_found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist '{playlist_id}' not found.")
        return result
