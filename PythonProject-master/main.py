import os
from pathlib import Path
import signal
from fastapi import FastAPI
from app.database import engine, Base, get_db
from app.Routes.AuthRoutes import router as AuthRoutes
from app.Routes.UserRoutes import router as UserRoutes
from app.Routes.StreamsRoutes import router as StreamRoutes
from app.Routes.SourceRoutes import router as SourceRoutes

from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount the static directory
from pathlib import Path

frontend_path = Path(__file__).parent / "Front"

recordings_path = Path(__file__).parent / "app" / "recordings"

app = FastAPI()

app.mount("/recordings", StaticFiles(directory=str(recordings_path)), name="recordings")
app.mount("/assets", StaticFiles(directory=frontend_path / "assets"), name="assets")
app.mount("/JS", StaticFiles(directory=frontend_path / "JS"), name="js")

@app.get("/")
async def read_index():
    return FileResponse(frontend_path / "index.html")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(AuthRoutes, prefix="/Auth", tags=["Auth"])
app.include_router(UserRoutes, prefix="/Users", tags=["Users"])
app.include_router(StreamRoutes, prefix="/Streams", tags=["Streams"])
app.include_router(SourceRoutes, prefix="/Sources", tags=["Sources"])

