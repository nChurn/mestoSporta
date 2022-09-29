import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Query

from utils.db_base import Base


class City(Base):
    __tablename__ = "cities"

    id = sa.Column(sa.BigInteger(), primary_key=True)
    name = sa.Column(sa.String(length=100), unique=True)
    is_active = sa.Column(sa.Boolean(), default=False)

    @classmethod
    async def get_all(cls, session_maker: sessionmaker):
        async with session_maker() as db_session:
            sql = sa.select(cls).where(cls.is_active == True)
            result = await db_session.execute(sql)
            cities = result.scalars().all()
        return cities

    @classmethod
    async def get_limited(cls, session_maker: sessionmaker, offset: int = 0):
        async with session_maker() as db_session:
            sql = sa.select(cls).where(cls.is_active == True).limit(5).offset(offset)
            result = await db_session.execute(sql)
            cities = result.scalars().all()
        return cities

    @classmethod
    async def add_city(
        cls, session_maker: sessionmaker, name: str, is_active: bool = False
    ):

        async with session_maker() as db_session:
            sql = sa.insert(cls).values(name=name, is_active=is_active).returning("*")
            res = await db_session.execute(sql)
            await db_session.commit()
            return res.first()

    # @classmethod
    # async def get_all(cls, session_maker: sessionmaker):
    #     async with session_maker() as db_session:
    #         sql = sa.select(cls).
