from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from core.config import settings
from auth.router import router as auth_router
from lobby.router import router as lobby_router
from game.router import router as game_router
from core.database import Base, engine


app = FastAPI(title=settings.PROJECT_NAME)

Base.metadata.create_all(bind=engine)

app.mount("/auth_static", StaticFiles(directory="auth/static"), name="auth_static")
app.mount("/lobby_static", StaticFiles(directory="lobby/static"), name="lobby_static")
app.mount("/game_static", StaticFiles(directory="game/static"), name="game_static")
templates = Jinja2Templates(directory="auth/templates")

app.include_router(auth_router)
app.include_router(lobby_router)
app.include_router(game_router)

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})
