from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, DateTime
from core.database import Base
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from auth.models import User


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner = relationship("User", back_populates="owned_rooms")
    participants = relationship("UserRoom", back_populates="room")


class UserRoom(Base):
    __tablename__ = "user_rooms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint('user_id', 'room_id', name='_user_room_uc'),)

    user = relationship("User", back_populates="joined_rooms")
    room = relationship("Room", back_populates="participants")
