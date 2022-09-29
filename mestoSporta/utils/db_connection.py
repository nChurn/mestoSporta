from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import DB
from utils.db_base import Base


async def create_db_session():
    engine = create_async_engine(
        f"postgresql+asyncpg://{DB['DB_USERNAME']}:{DB['DB_PASSWORD']}@{DB['DB_HOST']}:{DB['DB_PORT']}/{DB['DB_NAME']}",
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return async_session
