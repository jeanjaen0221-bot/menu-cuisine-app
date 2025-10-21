import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routers import reservations, menu_items, zenchef

load_dotenv()

app = FastAPI(title="FicheCuisineManager")

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(menu_items.router)
app.include_router(reservations.router)
app.include_router(zenchef.router)

# Ensure DB
init_db()

# Static serving for built frontend if available
backend_dir = Path(__file__).parent
frontend_dist = (backend_dir / "../frontend/dist").resolve()
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")
