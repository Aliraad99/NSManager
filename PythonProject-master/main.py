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


# Mount the static directory
recordings_path = Path(r"app\recordings")

app = FastAPI()

app.mount("/recordings", StaticFiles(directory=str(recordings_path)), name="recordings")
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

