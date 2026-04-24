import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class TeamResult(Base):
    __tablename__ = "team_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False)
    run_number = Column(Integer, nullable=False)
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    room = relationship("Room", back_populates="team_results")
    assignments = relationship("TeamAssignment", back_populates="result", cascade="all, delete-orphan")


class TeamAssignment(Base):
    __tablename__ = "team_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_id = Column(UUID(as_uuid=True), ForeignKey("team_results.id"), nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    team_number = Column(Integer, nullable=False)
    # 'playing' = paired with a teammate | 'waiting' = odd player out
    status = Column(SAEnum("playing", "waiting", name="assignment_status"), nullable=False, default="playing")

    result = relationship("TeamResult", back_populates="assignments")
    player = relationship("Player", back_populates="team_assignments")
