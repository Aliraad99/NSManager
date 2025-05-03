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
from pathlib import Path
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from app.Auth.Authentication import get_current_user  # Import your token validation function



frontend_path = Path(__file__).parent / "Front"
recordings_path = Path(__file__).parent / "app" / "recordings"

app = FastAPI()

app.mount("/recordings", StaticFiles(directory=str(recordings_path)), name="recordings")

app.mount("/assets", StaticFiles(directory=frontend_path / "assets"), name="assets")
app.mount("/JS", StaticFiles(directory=frontend_path / "JS"), name="js")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8010"],  # Replace with your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_login():
    return FileResponse(frontend_path / "login.html")


@app.get("/index.html")
async def read_index(request: Request):
    # Get the token from the cookie
    token = request.cookies.get("access_token")
    if not token:
        # Redirect to login if no token is found
        return RedirectResponse(url="/")
    
    try:
        # Validate the token
        get_current_user(token)
    except Exception:
        # Redirect to login if the token is invalid or expired
        return RedirectResponse(url="/")
    
    # Serve the index.html file if authenticated
    return FileResponse(frontend_path / "index.html")


@app.get("/Streams.html")
async def read_streams(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/")
    try:
        get_current_user(token)
    except Exception:
        return RedirectResponse(url="/")
    return FileResponse(frontend_path / "Streams.html")


@app.get("/Sources.html")
async def read_sources(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/")
    try:
        get_current_user(token)
    except Exception:
        return RedirectResponse(url="/")
    return FileResponse(frontend_path / "Sources.html")

app.include_router(AuthRoutes, prefix="/Auth", tags=["Auth"])
app.include_router(UserRoutes, prefix="/Users", tags=["Users"])
app.include_router(StreamRoutes, prefix="/Streams", tags=["Streams"])
app.include_router(SourceRoutes, prefix="/Sources", tags=["Sources"])
