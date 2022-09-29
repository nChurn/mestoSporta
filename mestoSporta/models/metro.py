from enum import unique
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from utils.db_base import Base


class Metro(Base):
    __tablename__ = "metros"

    id = sa.Column(sa.BigInteger(), primary_key=True)
    name = sa.Column(sa.String(length=100), unique=True)

    city = sa.Column(sa.String(length=100))

    @classmethod
    async def filter_by_city(
        cls, session_maker: sessionmaker, city: str, offset: int = 0
    ):
        async with session_maker() as db_session:
            sql = sa.select(cls).where(cls.city == city).limit(6).offset(offset)
            result = await db_session.execute(sql)
            metros = result.scalars().all()
        return metros

    @classmethod
    async def get_metro(cls, session_maker: sessionmaker, name):
        async with session_maker() as db_session:
            sql = sa.select(cls).where(cls.name == name)
            result = await db_session.execute(sql)
            metro = result.scalars().all()

        return metro

    @classmethod
    async def get_metro_by_id(cls, session_maker: sessionmaker, id):
        async with session_maker() as db_session:
            sql = sa.select(cls).where(cls.id == id)
            result = await db_session.execute(sql)
            metro = result.scalars().all()

        return metro

    @classmethod
    async def create(cls, session_maker: sessionmaker, name: str, city: str):
        async with session_maker() as db_session:
            sql = sa.insert(cls).values(name=name, city=city).returning("*")
            res = await db_session.execute(sql)
            await db_session.commit()
        return res.first()
