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

    work_status: Mapped[str] = mapped_column(SqlEnum(WorkTime))

    name_uz: Mapped[str] = mapped_column(VARCHAR(255))
    name_ru: Mapped[str] = mapped_column(VARCHAR(255))
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('admin_panel_users.id', ondelete='CASCADE'),
                                          nullable=True)
    lat: Mapped[float]
    long: Mapped[float]
    district_uz: Mapped[str]
    district_ru: Mapped[str]
    address_uz: Mapped[str]
    address_ru: Mapped[str]
    order_group_id: Mapped[int] = mapped_column(BigInteger)
    cart_number: Mapped[int] = mapped_column(BigInteger)
    photo: Mapped[ImageField] = mapped_column(ImageType(storage=FileSystemStorage('media/')))
    is_active: Mapped[bool] = mapped_column(nullable=False)
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


class CallCenters(BaseModel):
    shop_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('shops.id', ondelete='CASCADE'))
    contact: Mapped[str]
