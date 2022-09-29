import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, relationship


from utils.db_base import Base


class Traning(Base):
    __tablename__ = "tranings"

    id = sa.Column(sa.BigInteger(), primary_key=True)
    name = sa.Column(sa.String(length=100))

    is_active = sa.Column(sa.Boolean(), default=True)

    @classmethod
    async def get_limited(cls, session_maker: sessionmaker, offset: int = 0):
        async with session_maker() as db_session:
            sql = sa.select(cls).where(cls.is_active == True).limit(5).offset(offset)
            result = await db_session.execute(sql)
            tranings = result.scalars().all()
        return tranings
