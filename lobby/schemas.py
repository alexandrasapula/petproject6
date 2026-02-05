from pydantic import BaseModel


class RoomBase(BaseModel):
    name: str


class RoomCreate(RoomBase):
    pass


class RoomOut(RoomBase):
    id: int

    class Config:
        orm_mode = True


class JoinRoom(BaseModel):
    room_id: int
