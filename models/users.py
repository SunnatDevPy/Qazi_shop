from enum import Enum

from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import Boolean, select, desc
from sqlalchemy import ForeignKey, BIGINT, Enum as SqlEnum
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy_file import ImageField

from models.database import BaseModel, db


class MainPhoto(BaseModel):
    class LanguageBanner(str, Enum):
        UZ = 'uz'
        RU = 'ru'

    photo: Mapped[ImageField] = mapped_column(ImageType(storage=FileSystemStorage('media/')))
    language: Mapped[str] = mapped_column(SqlEnum(LanguageBanner), nullable=True)


class BotUser(BaseModel):
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    day_and_night: Mapped[bool] = mapped_column(Boolean, default=False)
    contact: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="False")

    def __str__(self):
        return super().__str__() + f" - {self.username}"


class AdminPanelUser(BaseModel):
    class StatusUser(str, Enum):
        ADMIN = 'admin'
        MODERATOR = 'moderator'

    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(SqlEnum(StatusUser), nullable=True)
    contact: Mapped[str] = mapped_column(nullable=True)
    day_and_night: Mapped[bool] = mapped_column(Boolean)
    is_active: Mapped[bool] = mapped_column(Boolean)

    def __str__(self):
        return super().__str__() + f" - {self.username}"

    @classmethod
    async def get_from_username(cls, username):
        query = select(cls).order_by(desc(cls.id)).filter(cls.username == username)
        return (await db.execute(query)).scalar()


class MyAddress(BaseModel):
    bot_user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("bot_users.id", ondelete='CASCADE'))
    address: Mapped[str] = mapped_column(String, nullable=True)
    lat: Mapped[float] = mapped_column(nullable=True)
    long: Mapped[float] = mapped_column(nullable=True)


class Cart(BaseModel):
    bot_user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("bot_users.id", ondelete='CASCADE'))
    product_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("shop_products.id", ondelete='CASCADE'))
    product_name_uz: Mapped[str]
    product_name_ru: Mapped[str]
    shop_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('shops.id', ondelete="CASCADE"))
    tip_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("product_tips.id", ondelete='CASCADE'))
    count: Mapped[int] = mapped_column()
    volume: Mapped[int]
    unit: Mapped[str]
    price: Mapped[int]
    total: Mapped[int]


class Order(BaseModel):
    class StatusOrder(str, Enum):
        NEW = "yangi"
        IS_GOING = "yig'ilmoqda"
        IN_PROGRESS = "yetkazilmoqda"
        DELIVERED = "yetkazildi"
        CANCELLED = "bekor qilindi"

    class Payment(str, Enum):
        CASH = "naqt"
        TERMINAL = "karta"

    payment: Mapped[bool] = mapped_column(SqlEnum(Payment), default=Payment.CASH.value)
    status: Mapped[str] = mapped_column(SqlEnum(StatusOrder))

    bot_user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('bot_users.id', ondelete='CASCADE'))
    address: Mapped[str] = mapped_column(String)
    shop_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('shops.id', ondelete="CASCADE"))
    first_last_name: Mapped[str] = mapped_column(String)
    contact: Mapped[str] = mapped_column(String)
    driver_price: Mapped[int] = mapped_column(BIGINT, default=0)
    total_sum: Mapped[int] = mapped_column(BIGINT)
    lat: Mapped[float]
    long: Mapped[float]

    @classmethod
    async def get_from_bot_user_in_type(cls, user_id, status):
        return ((await db.execute(
            select(cls).where(cls.bot_user_id == user_id, cls.status == status))).scalars().all())

    @classmethod
    async def get_from_bot_user_in_type_and_shop(cls, user_id, status, shop_id):
        return (await db.execute(select(cls).where(cls.bot_user_id == user_id, cls.status == status,
                                                   cls.shop_id == shop_id))).scalars().all()


class OrderItem(BaseModel):
    product_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("shop_products.id", ondelete='CASCADE'))
    order_id: Mapped[int] = mapped_column(BIGINT, ForeignKey(Order.id, ondelete='CASCADE'))
    count: Mapped[float] = mapped_column(default=1)
    volume: Mapped[int]
    unit: Mapped[str]
    price: Mapped[int]
    total: Mapped[int]


class ProjectAllStatus(BaseModel):
    day_and_night: Mapped[bool] = mapped_column(Boolean, default=False)


