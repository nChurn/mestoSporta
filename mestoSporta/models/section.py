import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, relationship


from utils.db_base import Base


class Section(Base):
    __tablename__ = "sections"
    id = sa.Column(sa.BigInteger, primary_key=True)

    title = sa.Column(sa.String(length=100))
    address = sa.Column(sa.String(length=128))

    category_id = sa.Column(sa.Integer, sa.ForeignKey("categories.id"))

    geoposition = sa.Column(sa.String(length=32), unique=True)

    metro_id = sa.Column(sa.Integer, sa.ForeignKey("metros.id"), nullable=True)
    district_id = sa.Column(sa.Integer, sa.ForeignKey("district.id"), nullable=True)
    is_active = sa.Column(sa.Boolean, default=False)

    stars = sa.Column(sa.Integer, default=0)
    rated_users_count = sa.Column(sa.Integer, default=0)
    city = sa.Column(sa.String(length=100))
    email = sa.Column(sa.String(length=100))
    user_id_id = sa.Column(sa.BigInteger, sa.ForeignKey("users.id"))
    tranings = sa.Column(sa.String(length=1000))

    @classmethod
    async def find(
        cls,
        session_maker: sessionmaker,
        city: str,
        category_id: str,
        district_id: str = None,
        metro_id: str = None,
    ):
        async with session_maker() as db_session:
            if district_id:
                sql = sa.select(cls).where(
                    cls.city == city,
                    cls.category_id == category_id,
                    cls.district_id == district_id,
                )
            else:
                sql = sa.select(cls).where(
                    cls.city == city,
                    cls.category_id == category_id,
                    cls.metro_id == metro_id,
                )

            result = await db_session.execute(sql)
            sections = result.scalars().all()
        return sections

    @classmethod
    async def find_user_sections(cls, session_maker, user_id):
        async with session_maker() as db_session:
            sql = sa.select(cls).where(cls.user_id_id == user_id)
            result = await db_session.execute(sql)
            sections = result.scalars().all()
        return sections

    @classmethod
    async def add(
        cls,
        session_maker: sessionmaker,
        title: str,
        address: str,
        category_id: int,
        geoposition: str,
        metro_id: int,
        district_id: int,
        city: str,
        email: str,
        user_id: int,
        tranings: str,
    ):
        async with session_maker() as db_session:
            sql = (
                sa.insert(cls)
                .values(
                    title=title,
                    address=address,
                    category_id=category_id,
                    geoposition=geoposition,
                    metro_id=metro_id,
                    district_id=district_id,
                    city=city,
                    email=email,
                    user_id_id=user_id,
                    tranings=tranings,
                )
                .returning("*")
            )
            res = await db_session.execute(sql)
            await db_session.commit()
            return res.first()

    async def find_by_id(cls, session_maker: sessionmaker, id: int):
        async with session_maker() as db_session:
            sql = sa.select(cls).where(cls.id == id)
            res = await db_session.execute(sql)
            sections = res.scalars().all()
        return sections[0]

    async def update_section_rates(self, session_maker: sessionmaker, rate: int):
        async with session_maker() as db_session:
            sql = (
                sa.update(Section)
                .where(Section.id == self.id)
                .values(
                    stars=self.stars + rate,
                    rated_users_count=self.rated_users_count + 1,
                )
            )
            result = await db_session.execute(sql)
            await db_session.commit()
        print("ok")
        return result


class SectionPhoto(Base):
    __tablename__ = "section_photos"
    id = sa.Column(sa.BigInteger, primary_key=True)

    file_path = sa.Column(sa.String(length=512))
    section = sa.Column(sa.Integer, sa.ForeignKey("sections.id"))

    @classmethod
    async def add(cls, session_maker: sessionmaker, file_path:str, section_id:int):
        async with session_maker() as db_session:
            sql = (
                sa.insert(cls)
                .values(
                    file_path=file_path,
                    section=section_id
                ).returning('*')
            )
            res =await db_session.execute(sql)
            await db_session.commit()
            return res.first()

    @classmethod
    async def get_by_section_id(cls, session_maker: sessionmaker, section_id: int):
        async with session_maker() as db_session:
            sql = (
                sa.select(cls)
                .where(
                    cls.section ==section_id
                )
            )
            result = await db_session.execute(sql)
            section_photos = result.scalars().all()
        return section_photos