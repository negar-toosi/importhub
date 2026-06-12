from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="ImportHub",
    lifespan=lifespan,
)


@app.get("/info")
async def info():
    return {"message": "ImportHub API"}