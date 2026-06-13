from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from src.core.database import create_db_and_tables
from src.app.apis.routers.upload_imports import router as imports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="ImportHub",
    lifespan=lifespan,
)

app.include_router(imports_router)


