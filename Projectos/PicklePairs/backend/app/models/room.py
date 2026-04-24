import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_code = Column(String(4), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, default="Pickleball Fun Room")
    creator_token = Column(String(64), nullable=False)
    status = Column(SAEnum("open", "closed", name="room_status"), nullable=False, default="open")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    players = relationship("Player", back_populates="room", cascade="all, delete-orphan")
    team_results = relationship("TeamResult", back_populates="room", cascade="all, delete-orphan")
