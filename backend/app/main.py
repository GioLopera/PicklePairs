from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import rooms, players, teams
from app.websockets.room_ws import router as ws_router

app = FastAPI(
    title="PicklePairs API",
    description="Room-based random pickleball team generator",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rooms.router)
app.include_router(players.router)
app.include_router(teams.router)
app.include_router(ws_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
