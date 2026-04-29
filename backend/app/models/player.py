import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False)
    name = Column(String(50), nullable=False)
    joined_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    room = relationship("Room", back_populates="players")
    team_assignments = relationship("TeamAssignment", back_populates="player")

    __table_args__ = (
        UniqueConstraint("room_id", "name", name="uq_player_name_per_room"),
    )
