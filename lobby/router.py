from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from auth.deps import get_current_user
from core.database import get_db
from lobby.models import Room, UserRoom
from sqlalchemy.orm import Session
from lobby.schemas import RoomCreate, RoomOut, JoinRoom


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

    user_room = UserRoom(user_id=current_user.id, room_id=db_room.id)
    db.add(user_room)
    db.commit()

    return db_room


@router.post("/api/join-room")
def join_room(data: JoinRoom, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    room_id = data.room_id
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    existing = db.query(UserRoom).filter_by(user_id=current_user.id, room_id=room_id).first()
    if existing:
        return {"room_id": room_id}

    user_room = UserRoom(user_id=current_user, room_id=room_id)
    db.add(user_room)
    db.commit()
    return {"room_id": room_id}


@router.get("/room/{room_id}")
def room_page(request: Request, room_id: int):
    return templates.TemplateResponse("room.html", {"request": request, "room_id": room_id})


@router.get("/api/room/{room_id}/data")
def room_data(room_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user_room = db.query(UserRoom).filter_by(user_id=current_user.id, room_id=room_id).first()
    if not user_room:
        raise HTTPException(status_code=403, detail="Not allowed in this room")

    room = db.query(Room).filter(Room.id == room_id).first()
    return {
        "room_id": room.id,
        "room_name": room.name,
        "user_id": current_user.id,
        "username": current_user.username
    }
