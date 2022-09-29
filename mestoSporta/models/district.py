from enum import unique
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from utils.db_base import Base


class District(Base):
    __tablename__ = "district"

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
            districts = result.scalars().all()

        return districts

    @classmethod
    async def get_district(cls, session_maker: sessionmaker, name):
        async with session_maker() as db_session:
            sql = sa.select(cls).where(cls.name == name)
            result = await db_session.execute(sql)
            district = result.scalars().all()

        return district

    @classmethod
    async def get_district_by_id(cls, session_maker: sessionmaker, id):
        async with session_maker() as db_session:
            sql = sa.select(cls).where(cls.id == id)
            result = await db_session.execute(sql)
            district = result.scalars().all()

        return district

    @classmethod
    async def create(cls, session_maker: sessionmaker, name: str, city: str):
        async with session_maker() as db_session:
            sql = sa.insert(cls).values(name=name, city=city).returning("*")
            res = await db_session.execute(sql)
            await db_session.commit()
        return res.first()
