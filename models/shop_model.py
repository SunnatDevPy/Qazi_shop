from enum import Enum

from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import BigInteger, Enum as SqlEnum, VARCHAR, ForeignKey, select, desc, Integer, JSON, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy_file import ImageField

from models.database import BaseModel, db


class Shop(BaseModel):
    class WorkTime(str, Enum):
        OPEN = 'ochiq'
        CLOSE = 'yopiq'

    name_uz: Mapped[str] = mapped_column(VARCHAR(255))
    name_ru: Mapped[str] = mapped_column(VARCHAR(255))
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('admin_panel_users.id', ondelete='CASCADE'),
                                          nullable=True)
    work_status: Mapped[str] = mapped_column(SqlEnum(WorkTime), nullable=True)
    lat: Mapped[float] = mapped_column(nullable=True)
    long: Mapped[float] = mapped_column(nullable=True)
    district_uz: Mapped[str] = mapped_column(nullable=True)
    district_ru: Mapped[str] = mapped_column(nullable=True)
    address_uz: Mapped[str] = mapped_column(nullable=True)
    address_ru: Mapped[str] = mapped_column(nullable=True)
    order_group_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    cart_number: Mapped[int] = mapped_column(BigInteger, nullable=True)
    photo: Mapped[ImageField] = mapped_column(ImageType(storage=FileSystemStorage('media/')), nullable=True)
    is_active: Mapped[bool]
    work: Mapped[list['WorkTimes']] = relationship('WorkTimes', lazy='selectin', back_populates='shop')


    @classmethod
    async def get_shops_from_user(cls, id_):
        query = select(cls).order_by(desc(cls.id)).filter(cls.owner_id == id_)
        return (await db.execute(query)).scalars().all()


class WorkTimes(BaseModel):
    shop_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('shops.id', ondelete='CASCADE'))
    open_time: Mapped[str]
    close_time: Mapped[str]
    weeks: Mapped[list] = mapped_column(JSON)
    shop: Mapped[list['Shop']] = relationship('Shop', lazy='selectin', back_populates='work')
