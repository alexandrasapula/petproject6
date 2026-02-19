from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from auth.deps import get_current_user
from core.database import get_db
from lobby.models import Room, UserRoom
from sqlalchemy.orm import Session
from auth.models import User
from .services.service import game_start_logic


router = APIRouter(prefix="/game", tags=["game"])
templates = Jinja2Templates(directory="game/templates")


@router.get("/room/{room_id}")
def room_page(request: Request, room_id: int):
    return templates.TemplateResponse("room.html", {"request": request, "room_id": room_id})


@router.get("/api/room/{room_id}/data")
def room_data(room_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user_room = db.query(UserRoom).filter_by(user_id=current_user.id, room_id=room_id).first()
    if not user_room:
        raise HTTPException(status_code=403, detail="Not allowed in this room")

    room = db.query(Room).filter(Room.id == room_id).first()
    players = (db.query(UserRoom).filter(UserRoom.room_id == room_id).join(User).order_by(UserRoom.seat_number).all())
    return {
        "room_id": room.id,
        "room_name": room.name,
        "status": room.status,
        "user_id": current_user.id,
        "seat_number": user_room.seat_number,
        "is_owner": user_room.seat_number == 1,
        "players": [
            {
                "id": ur.user.id,
                "username": ur.user.username,
                "seat_number": ur.seat_number
            }
            for ur in players
        ]
    }


@router.post("/api/room/{room_id}/start")
def start_room_game(room_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    room = db.query(Room).get(room_id)

    owner = db.query(UserRoom).filter_by(room_id=room_id, user_id=current_user.id, seat_number=1).first()
    if not owner:
        raise HTTPException(403)

    players_count = db.query(UserRoom).filter_by(room_id=room_id).count()
    if players_count < 2:
        raise HTTPException(400, "Not enough players")

    game_start_logic(room.id, db)


@router.get("/play/{roomId}")
def game_page(request: Request, room_id: int):
    return templates.TemplateResponse("game.html", {"request": request, "room_id": room_id})
