from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.routers import lessons


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Dispose engine on shutdown
    await engine.dispose()


app = FastAPI(
    title="PocketWise API",
    description="Backend για την εφαρμογή χρηματοοικονομικού αλφαβητισμού PocketWise",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow frontend dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(lessons.router)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "PocketWise API is running 🚀"}


@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "ok"}