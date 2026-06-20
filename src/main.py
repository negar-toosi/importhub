from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.apis.routers.imports import router as imports_router
from src.apis.routers.shipments import router as shipments_router
from src.infrastructure.database import engine, Base
@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.infrastructure.tables import Import, ImportError, ShipmentRecord
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="ImportHub",
    lifespan=lifespan,
)

app.include_router(imports_router)
app.include_router(shipments_router)


