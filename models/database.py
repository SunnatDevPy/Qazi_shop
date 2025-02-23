import logging
from _ctypes_test import func
from datetime import datetime

from faker import Faker
from sqlalchemy import BigInteger, delete as sqlalchemy_delete, DateTime, update as sqlalchemy_update, func, desc
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncAttrs
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, selectinload

from config import conf


class Base(AsyncAttrs, DeclarativeBase):

    @declared_attr
    def __tablename__(self) -> str:
        __name = self.__name__[:1]
        for i in self.__name__[1:]:
            if i.isupper():
                __name += '_'
            __name += i
        __name = __name.lower()

        if __name.endswith('y'):
            __name = __name[:-1] + 'ie'
        return __name + 's'


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self):
        self._engine = create_async_engine(conf.db.db_url)
        self._session = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)()

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    # async def execute(self, stmt):
    #     try:
    #         result = await self._session.execute(stmt)
    #         await self._session.commit()
    #         return result
    #     except Exception as e:
    #         logging.error(f"Ошибка SQLAlchemy: {e}")
    #         await self._session.rollback()
    #         raise


db = AsyncDatabaseSession()
db.init()


# ----------------------------- ABSTRACTS ----------------------------------
class AbstractClass:
    @staticmethod
    async def commit():
        try:
            await db.commit()
        except Exception as e:
            print(e)
            await db.rollback()

    @classmethod
    async def create(cls, **kwargs):  # Create
        try:
            object_ = cls(**kwargs)
            db.add(object_)
            await cls.commit()
            return object_
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def update(cls, id_, **kwargs):
        try:
            query = (
                sqlalchemy_update(cls)
                .where(cls.id == id_)
                .values(**kwargs)
                .execution_options(synchronize_session="fetch")
            )
            await db.execute(query)
            await cls.commit()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def get(cls, _id, *, relationship=None):
        try:
            query = select(cls).where(cls.id == _id)
            if relationship:
                query = query.options(selectinload(relationship))
            return (await db.execute(query)).scalar()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def get_from_username(cls, user_name, *, relationship=None):
        try:
            query = select(cls).where(cls.username == user_name)
            if relationship:
                query = query.options(selectinload(relationship))
            return (await db.execute(query)).scalar()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def from_user(cls, _id, *, relationship=None):
        try:
            query = select(cls).where(cls.bot_user_id == _id).order_by(desc(cls.id))
            if relationship:
                query = query.options(selectinload(relationship))
            return (await db.execute(query)).scalars()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def get_shop_product_id(cls, product_id, shop_id, *, relationship=None):
        try:
            query = select(cls).where(cls.id == product_id, cls.shop_id == shop_id).order_by(desc(cls.id))
            if relationship:
                query = query.options(selectinload(relationship))
            return (await db.execute(query)).scalars()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def from_user_order(cls, _id, *, relationship=None):
        try:
            query = select(cls).where(cls.user_id == _id).order_by(desc(cls.id))
            if relationship:
                query = query.options(selectinload(relationship))
            return (await db.execute(query)).scalar()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def count(cls):
        query = select(func.count()).select_from(cls)
        return (await db.execute(query)).scalar()

    @classmethod
    async def generate(cls, count: int = 1):
        return Faker()

    @classmethod
    async def delete(cls, id_):
        try:
            query = sqlalchemy_delete(cls).where(cls.id == id_)
            await db.execute(query)
            await cls.commit()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def filter(cls, criteria, *, relationship=None, columns=None):
        try:
            if columns:
                query = select(*columns)
            else:
                query = select(cls)

            query = query.where(criteria)

            if relationship:
                query = query.options(selectinload(relationship))
            return (await db.execute(query)).scalars()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def all(cls):
        try:
            return (await db.execute(select(cls))).scalars().all()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def get_cart_from_shop(cls, user_id, shop_id):
        try:
            return (
                await db.execute(select(cls).where(cls.bot_user_id == user_id, cls.shop_id == shop_id))).scalars().all()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def get_from_shop(cls, shop_id):
        try:
            return (await db.execute(select(cls).where(cls.shop_id == shop_id))).scalars().all()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def from_shop(cls, shop_id):
        try:
            return (await db.execute(select(cls).where(cls.shop_id == shop_id))).scalars().all()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def get_cart_from_product(cls, user_id, product_id):
        try:
            return (
                await db.execute(select(cls).where(cls.bot_user_id == user_id, cls.product_id == product_id))).scalar()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def get_from_bot_user(cls, user_id):
        try:
            return (await db.execute(select(cls).where(cls.bot_user_id == user_id))).scalars().all()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def get_order_items(cls, order_id):
        try:
            return (await db.execute(select(cls).where(cls.order_id == order_id))).scalars().all()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def get_from_name(cls, address):
        try:
            return (await db.execute(select(cls).where(cls.address == address))).scalars().all()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []

    @classmethod
    async def search_shops(cls, name, category_id=None):
        try:
            if category_id:
                return (await db.execute(
                    select(cls).where(cls.category_id == category_id, cls.name_uz.ilike(f"%{name}%")))).scalars().all()
            else:
                return (await db.execute(select(cls).filter(cls.name_uz.ilike(f"%{name}%")))).scalars().all()
        except DBAPIError as e:
            await db.rollback()  # Откат транзакции
            print(f"Ошибка базы данных: {e}")
            return []
    # def run_async(self, func, *args, **kwargs):
    #     return asyncio.run(func(*args, **kwargs))

    # def convert_uzs(self, amount: int):
    #     return amount * current_price
    #
    # def convert_usd(self, amount: int):
    #     return amount // current_price


class BaseModel(Base, AbstractClass):
    __abstract__ = True
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    def __str__(self):
        return f"{self.id}"


class CreatedBaseModel(BaseModel):
    __abstract__ = True
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
