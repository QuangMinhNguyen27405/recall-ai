from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config.settings import settings

engine = create_async_engine(settings.database_url, future=True, poolclass=NullPool)
AsyncSessionLocal = async_sessionmaker[AsyncSession](
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
