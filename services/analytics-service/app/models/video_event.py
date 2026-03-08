import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, Enum as SAEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EventType(str, PyEnum):
    play = "play"
    pause = "pause"
    seek = "seek"
    complete = "complete"


class VideoEvent(Base):
    __tablename__ = "video_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    video_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_type: Mapped[EventType] = mapped_column(SAEnum(EventType, name="event_type_enum"), nullable=False)
    position_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True,
    )

    def __repr__(self) -> str:
        return f"<VideoEvent user={self.user_id} video={self.video_id} event={self.event_type}>"
