from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .config import get_settings
from .routers import logs_router, admin_router, requests_router, agents_router, billing_router, auth_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (for development)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="PromptLab API",
    description="Prompt testing and optimization platform API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware - secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin_router)
app.include_router(logs_router)
app.include_router(requests_router)
app.include_router(agents_router)
app.include_router(billing_router)
app.include_router(auth_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
