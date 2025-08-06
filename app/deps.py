from typing import Annotated, AsyncGenerator

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import engine



async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session = AsyncSession(engine, expire_on_commit=True)
    try:
        yield session
    finally:
        await session.close()


SessionDep = Annotated[AsyncSession, Depends(get_db)]