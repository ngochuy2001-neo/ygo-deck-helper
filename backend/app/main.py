from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.database import check_database_connection, dispose_engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Khởi tạo / đóng tài nguyên khi app start/stop."""
    settings.card_images_dir.mkdir(parents=True, exist_ok=True)
    yield
    await dispose_engine()


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)

app.mount(
    "/static/cards",
    StaticFiles(directory=str(settings.card_images_dir)),
    name="card_images",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    db_ok = await check_database_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
    }
