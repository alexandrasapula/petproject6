from fastapi import Depends
from core.database import get_db
from sqlalchemy.orm import Session
from lobby.models import Room


def game_start_logic(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    room.status = "started"
    db.commit()
