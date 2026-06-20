from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, AsyncSession, async_sessionmaker
from src.infrastructure.config import settings
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass



# async def get_session():
#     async with AsyncSessionLocal() as session:
#         yield session
# SessionDep = Annotated[AsyncSession, Depends(get_session)]