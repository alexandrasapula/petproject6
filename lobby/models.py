from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, DateTime
from core.database import Base
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from auth.models import User
from sqlalchemy import Enum
import enum


class RoomStatus(str, enum.Enum):
    waiting = "waiting"
    playing = "playing"
    finished = "finished"


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(RoomStatus), default=RoomStatus.waiting, nullable=False, server_default=RoomStatus.waiting.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner = relationship("User", back_populates="owned_rooms")
    participants = relationship("UserRoom", back_populates="room")


class UserRoom(Base):
    __tablename__ = "user_rooms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    seat_number = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'room_id', name='_user_room_uc'),
        UniqueConstraint('room_id', 'seat_number', name='_room_seat_uc'),
    )

    user = relationship("User", back_populates="joined_rooms")
    room = relationship("Room", back_populates="participants")
