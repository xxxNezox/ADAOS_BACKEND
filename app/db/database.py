from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings 

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    echo=True,
    poolclass=NullPool
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False
)

async def get_db():
    async with SessionLocal() as session:
        yield session

Base = declarative_base()