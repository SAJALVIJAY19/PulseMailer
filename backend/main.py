from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routes.generate import router as generate_router
from routes.history import router as history_router
from routes.stats import router as stats_router
from scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
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


@app.get("/")
async def root():
    return {"status": "MailCraft AI is running"}
