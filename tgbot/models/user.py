from sqlalchemy import Column, String, BigInteger, insert, update, func, select
from sqlalchemy.orm import sessionmaker

from tgbot.services.db_base import Base


class TGUser(Base):
    """Telegram user model"""

    __tablename__ = "telegram_users"
    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    firstname = Column(String(length=100))
    lastname = Column(String(length=100))
    username = Column(String(length=100), nullable=True)
    phone = Column(String(length=15), nullable=True)
    lang_code = Column(String(length=10), default="en")

    @classmethod
    async def get_user(
        cls, db_session: sessionmaker, telegram_id: int
    ) -> "TGUser":
        """Get user by telegram_id"""
        async with db_session() as session:
            result = await session.execute(
                select(TGUser).filter(TGUser.telegram_id == telegram_id)
            )
            return result.scalars().first()

    @classmethod
    async def add_user(
        cls,
        db_session: sessionmaker,
        telegram_id: int,
        firstname: str,
        lastname: str,
        username: str = None,
        phone: str = None,
        lang_code: str = None,
    ) -> "TGUser":
        """Add new user into DB"""
        async with db_session() as session:
            result = await session.execute(
                insert(TGUser)
                .values(
                    telegram_id=telegram_id,
                    firstname=firstname,
                    lastname=lastname,
                    username=username,
                    phone=phone,
                    lang_code=lang_code,
                )
                .returning("*")
            )
            await session.commit()
            return await cls.get_user(db_session, result.scalars().first())

    @classmethod
    async def update_user(
        cls, db_session: sessionmaker, telegram_id: int, updated_fields: dict
    ) -> "TGUser":
        """Update user fields"""
        async with db_session() as session:
            result = await session.execute(
                update(TGUser)
                .where(TGUser.telegram_id == telegram_id)
                .values(**updated_fields)
                .returning("*")
            )
            await session.commit()
            return await cls.get_user(db_session, result.scalars().first())

    @classmethod
    async def get_all_users(cls, db_session: sessionmaker) -> list:
        """Returns all users from DB"""
        async with db_session() as session:
            result = await session.execute(select(TGUser))
            return result.scalars().all()

    @classmethod
    async def get_users_by_lang_code(
        cls, db_session: sessionmaker, lang_code: str
    ) -> list:
        """Returns all users from DB"""
        async with db_session() as session:
            result = await session.execute(
                select(TGUser).filter(TGUser.lang_code == lang_code)
            )
            return result.scalars().all()

    @classmethod
    async def get_users_count_by_lang_code(
        cls, db_session: sessionmaker, lang_code: str
    ) -> int:
        """Returns all users from DB"""
        async with db_session() as session:
            result = await session.execute(
                select(func.count(TGUser.id)).filter(
                    TGUser.lang_code == lang_code
                )
            )
            return result.scalar()

    @classmethod
    async def users_count(cls, db_session: sessionmaker) -> int:
        """Counts all users in the database"""
        async with db_session() as session:
            result = await session.execute(select(func.count(TGUser.id)))
            return result.scalar()

    def __repr__(self):
        return (
            f"User (ID: {self.telegram_id} - {self.firstname} {self.lastname})"
        )
