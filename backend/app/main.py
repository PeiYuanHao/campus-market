import os
from pathlib import Path
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError

from app.db.database import Base, SessionLocal, engine
from app.routes.ai import router as ai_router
from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.categories import router as categories_router
from app.routes.favorites import router as favorites_router
from app.routes.items import router as items_router
from app.services.bootstrap import migrate_database
from app.services.seed import seed_data


app = FastAPI(title="Campus Market Demo", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(categories_router)
app.include_router(items_router)
app.include_router(favorites_router)
app.include_router(ai_router)


PROJECT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_DIR / "frontend"


@app.on_event("startup")
def on_startup():
    startup_delay = float(os.getenv("STARTUP_DELAY", "0"))
    if startup_delay > 0:
        time.sleep(startup_delay)

    for attempt in range(3):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except OperationalError as exc:
            if "already exists" not in str(exc) or attempt == 2:
                raise
            time.sleep(1)
    migrate_database(engine)
    with SessionLocal() as db:
        seed_data(db)


@app.get("/health")
def health():
    return {"status": "ok"}


if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/account")
def account():
    return FileResponse(FRONTEND_DIR / "account.html")
