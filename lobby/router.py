from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from auth.deps import get_current_user
from core.database import get_db
from lobby.models import Room, UserRoom
from sqlalchemy.orm import Session
from lobby.schemas import RoomCreate, RoomOut, JoinRoom
from game.services.service import game_start_logic


router = APIRouter(prefix="/lobby", tags=["lobby"])
templates = Jinja2Templates(directory="lobby/templates")


@router.get("/")
def lobby_page(request: Request):
    return templates.TemplateResponse("lobby.html", {"request": request})


@router.get("/api/lobby-data")
def lobby_data(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rooms = db.query(Room).all()
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "rooms": [{"id": r.id, "name": r.name} for r in rooms]
    }


@router.post("/api/create-room", response_model=RoomOut)
def create_room(room: RoomCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_room = Room(name=room.name, owner_id=current_user.id)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)

    user_room = UserRoom(user_id=current_user.id, room_id=db_room.id, seat_number=1)
    db.add(user_room)
    db.commit()

    return db_room


@router.post("/api/join-room")
def join_room(data: JoinRoom, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    room_id = data.room_id
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if (db.query(UserRoom).filter_by(user_id=current_user.id, room_id=room_id).first()):
        return {"room_id": room_id}

    taken_seats = db.query(UserRoom.seat_number).filter(UserRoom.room_id == room_id).all()
    taken_seats = {s[0] for s in taken_seats}
    seat_number = next((seat for seat in range(2, 7) if seat not in taken_seats), None)
    if seat_number is None:
        raise HTTPException(status_code=400, detail="Room is full")

    user_room = UserRoom(user_id=current_user.id, room_id=room_id, seat_number=seat_number)
    db.add(user_room)
    db.commit()
    players_count = db.query(UserRoom).filter_by(room_id=room_id).count()
    if players_count == 6:
        game_start_logic(room.id, db)
    return {"room_id": room_id}
