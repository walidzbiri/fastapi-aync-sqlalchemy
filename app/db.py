from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:changeme@postgres/postgres"

# connect_args is ONLY for sqlite, remove if using PostgreSQL or other.
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

Base = declarative_base()