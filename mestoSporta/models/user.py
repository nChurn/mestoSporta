import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from datetime import datetime, timedelta

from utils.db_base import Base


class User(Base):
    __tablename__ = "users"
    telegram_id = sa.Column(sa.BigInteger, primary_key=True)
    first_name = sa.Column(sa.String(length=100))
    last_name = sa.Column(sa.String(length=100), nullable=True)
    username = sa.Column(sa.String(length=100), nullable=True)
    lang_code = sa.Column(sa.String(length=4), default="ru_RU")
    role = sa.Column(sa.String(length=100), default="user")

    is_subscribe = sa.Column(sa.Boolean(), default=False)
    expires_in = sa.Column(sa.DateTime(), nullable=True)

    @classmethod
    async def get_user(cls, session_maker: sessionmaker, telegram_id: int):
        async with session_maker() as db_session:
            sql = sa.select(cls).where(cls.telegram_id == telegram_id)
            request = await db_session.execute(sql)
            user: cls = request.scalar()
        return user

    @classmethod
    async def add_user(
        cls,
        session_maker: sessionmaker,
        telegram_id: int,
        first_name: str,
        last_name: str,
        lang_code: str = None,
        username: str = None,
        role: str = None,
    ):

        async with session_maker() as db_session:
            sql = (
                sa.insert(cls)
                .values(
                    telegram_id=telegram_id,
                    first_name=first_name,
                    last_name=last_name,
                    lang_code=lang_code,
                    username=username,
                    role=role,
                )
                .returning("*")
            )
            res = await db_session.execute(sql)
            await db_session.commit()
            return res.first()

    async def update_user(self, session_maker: sessionmaker, updated_fields: dict):
        async with session_maker() as db_session:
            sql = (
                sa.update(User)
                .where(User.telegram_id == self.telegram_id)
                .values(**updated_fields)
            )
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    async def set_subscribtion(self, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = (
                sa.update(User)
                .where(User.telegram_id == self.telegram_id)
                .values(
                    is_subscribe=True, expires_in=datetime.now() + timedelta(days=30)
                )
            )
            result = await db_session.execute(sql)
            await db_session.commit()
            return result
