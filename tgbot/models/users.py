from sqlalchemy import Column, insert, String, BigInteger, Integer, BOOLEAN, ForeignKey, update, func
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.sqltypes import BigInteger

from tgbot.services.db_base import Base


class User(Base):
    __tablename__ = "telegram_users"
    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(String(length=50), unique=True)
    fullname = Column(String(length=200))
    username = Column(String(length=100), nullable=True)
    phone = Column(String(length=15), nullable=True)
    status = Column(String(length=15), nullable=True)
    ids_count = Column(Integer, default=0)
    follow_status = Column(BOOLEAN, default=False)
    lang_code = Column(String(length=10), default='ru_RU')
    role = Column(String(length=100), default='user')

    @classmethod
    async def get_user(cls, db_session: sessionmaker, telegram_id: str) -> 'User':
        async with db_session() as db_session:
            sql = select(cls).where(cls.telegram_id == telegram_id)
            request = await db_session.execute(sql)
            user: cls = request.scalar()
        return user

    @classmethod
    async def add_user(cls,
                       db_session: sessionmaker,
                       telegram_id: str,
                       fullname: str,
                       username: str = None,
                       phone: str = None,
                       lang_code: str = None,
                       role: str = None
                       ) -> 'User':
        async with db_session() as db_session:
            sql = insert(cls).values(telegram_id=telegram_id,
                                     fullname=fullname,
                                     username=username,
                                     phone=phone,
                                     lang_code=lang_code,
                                     role=role).returning('*')
            result = await db_session.execute(sql)
            await db_session.commit()
            return result.first()

    async def update_user(self, db_session: sessionmaker, updated_fields: dict) -> 'User':
        async with db_session() as db_session:
            sql = update(User).where(User.telegram_id ==
                                     self.telegram_id).values(**updated_fields)
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    async def increment_ids_count(self, db_session: sessionmaker):
        async with db_session() as db_session:
            sql = update(User).where(
                User.telegram_id == self.telegram_id
            ).values(
                ids_count=User.ids_count + 1
            )
            await db_session.execute(sql)
            await db_session.commit()

    @classmethod
    async def get_top_users(cls, db_session: sessionmaker, limit: int = 10) -> list:
        async with db_session() as db_session:
            sql = select(cls.telegram_id, cls.fullname, cls.ids_count).order_by(
                User.ids_count.desc()
            ).limit(limit)
            request = await db_session.execute(sql)
            users: list = request.fetchall()
        return users

    @classmethod
    async def get_all_users(cls, db_session: sessionmaker) -> list:
        async with db_session() as db_session:
            sql = select(cls.id, cls.telegram_id,
                         cls.fullname, cls.username, cls.phone,
                         cls.follow_status, cls.status).order_by(
                User.id.asc()
            )
            result = await db_session.execute(sql)
            users = result.fetchall()
        return users

    @classmethod
    async def users_count(cls, db_session: sessionmaker) -> int:
        async with db_session() as db_session:
            sql = select([func.count(cls.id)]).select_from(cls)
            request = await db_session.execute(sql)
            count = request.scalar()
        return count

    @classmethod
    async def count_referrals(cls, db_session: sessionmaker, user: "User"):
        async with db_session() as db_session:
            sql = select(
                func.count(Referral.telegram_id)
            ).where(
                Referral.referrer_id == user.telegram_id
            ).join(
                User
            ).group_by(
                Referral.referrer_id
            )
            result = await db_session.execute(sql)
            return result.scalar()

    def __repr__(self):
        return f'User (ID: {self.telegram_id} - {self.fullname})'


class Referral(Base):
    __tablename__ = "referral_users"
    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(String, unique=True)
    referrer_id = Column(ForeignKey(User.telegram_id, ondelete='CASCADE'))

    @classmethod
    async def add_user(cls,
                       db_session: sessionmaker,
                       telegram_id: str,
                       referrer_id: str
                       ) -> 'User':
        async with db_session() as db_session:
            sql = insert(cls).values(
                telegram_id=telegram_id,
                referrer_id=referrer_id
            )
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def find_referrer(cls, db_session: sessionmaker, telegram_id: str) -> str:
        async with db_session() as db_session:
            sql = select(cls.referrer_id).where(cls.telegram_id == telegram_id)
            result = await db_session.execute(sql)
        return result.first()


class ID(Base):
    __tablename__ = "users_ids"
    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(ForeignKey(User.telegram_id, ondelete='CASCADE'))

    @classmethod
    async def add_user_id(cls,
                          db_session: sessionmaker,
                          telegram_id: str,
                          ) -> 'ID':
        async with db_session() as db_session:
            sql = insert(cls).values(
                telegram_id=telegram_id,
            ).returning('*')
            result = await db_session.execute(sql)
            await db_session.commit()
            return result.first()

    @classmethod
    async def get_ids(cls, db_session: sessionmaker, telegram_id: str) -> list:
        async with db_session() as db_session:
            sql = select(
                cls.id
            ).where(
                ID.telegram_id == telegram_id
            ).order_by(
                cls.id.asc()
            )
            request = await db_session.execute(sql)
            ids = request.fetchall()
        return ids

    @classmethod
    async def get_ids_with_user_model(cls, db_session: sessionmaker) -> list:
        async with db_session() as db_session:
            sql = select(
                cls.id,
                User.fullname,
                User.username,
                User.phone,
                User.follow_status,
            ).join(
                User
            ).order_by(
                cls.id.asc()
            )
            request = await db_session.execute(sql)
            ids = request.fetchall()
        return ids
