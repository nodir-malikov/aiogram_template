from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from sqlalchemy_utils import database_exists, create_database

from tgbot.config import Config
from tgbot.services.db_base import Base


async def create_db_session(config: Config) -> AsyncSession:
    """Create DB session"""
    auth_data = f"{config.db.user}:{config.db.password}" \
        f"@{config.db.host}:{config.db.port}/{config.db.database}"

    db_uri = f"postgresql://{auth_data}"
    if not database_exists(db_uri):
        # create database if not exists
        create_database(db_uri)

    db_uri = f"postgresql+asyncpg://{auth_data}"
    engine = create_async_engine(
        db_uri,
        future=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # expire_on_commit=False will prevent attributes from being expired
    # after commit.
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    return async_session
