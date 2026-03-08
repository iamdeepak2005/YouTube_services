import uuid

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    youtube_video_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    playlist_id: Mapped[str] = mapped_column(String(36), ForeignKey("playlists.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail: Mapped[str] = mapped_column(String(500), nullable=True)
    duration: Mapped[int] = mapped_column(Integer, default=0)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    playlist: Mapped["Playlist"] = relationship("Playlist", back_populates="videos")

    def __repr__(self) -> str:
        return f"<Video youtube_id={self.youtube_video_id} pos={self.position}>"
