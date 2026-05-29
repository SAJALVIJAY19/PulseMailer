from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from routes.generate import router as generate_router
from routes.history import router as history_router
from routes.stats import router as stats_router
from scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-initialize database tables in Supabase on startup
    try:
        from database import init_db
        init_db()
        print("PostgreSQL Database tables verified/created successfully!")
    except Exception as e:
        print(f"Warning: Could not initialize database on startup: {e}")

    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="PulseMailer", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router, prefix="/generate")
app.include_router(history_router, prefix="/history")
app.include_router(stats_router, prefix="/stats")


# Dynamic path resolution for robust static page serving
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")


@app.get("/")
@app.get("/landing.html")
async def serve_landing():
    return FileResponse(os.path.join(FRONTEND_DIR, "landing.html"))


@app.get("/index.html")
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/dashboard.html")
async def serve_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))


@app.get("/analytics.html")
async def serve_analytics():
    return FileResponse(os.path.join(FRONTEND_DIR, "analytics.html"))

