from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import BigInteger, String, VARCHAR, ForeignKey, select
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy_file import ImageField

from models.database import BaseModel, db


class ShopCategory(BaseModel):
    name_uz: Mapped[str] = mapped_column(VARCHAR(255))
    name_ru: Mapped[str] = mapped_column(VARCHAR(255))
    shop_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('shops.id', ondelete='CASCADE'),
                                         nullable=True)
    parent_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('shop_categories.id', ondelete='CASCADE'),
                                           nullable=True)
    photo: Mapped[ImageField] = mapped_column(ImageType(storage=FileSystemStorage('media/')), nullable=True)

    @classmethod
    async def get_shop_categories(cls, id_):
        query = select(cls).filter(cls.shop_id == id_)
        return (await db.execute(query)).scalars().all()

    @classmethod
    async def get_from_shop(cls, shop_id, category_id):
        query = select(cls).filter(cls.shop_id == shop_id, cls.id == category_id)
        return (await db.execute(query)).scalars().all()


class ShopProduct(BaseModel):
    name_uz: Mapped[str] = mapped_column(VARCHAR(255))
    name_ru: Mapped[str] = mapped_column(VARCHAR(255))
    description_uz: Mapped[str] = mapped_column(String(255), nullable=True)
    description_ru: Mapped[str] = mapped_column(String(255), nullable=True)
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('admin_panel_users.id', ondelete='CASCADE'))
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(ShopCategory.id, ondelete='CASCADE'))
    photo: Mapped[ImageField] = mapped_column(ImageType(storage=FileSystemStorage('media/')), nullable=True)
    shop_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('shops.id', ondelete='CASCADE'), nullable=True)

    @classmethod
    async def get_products_category(cls, category_id):
        query = select(cls).filter(cls.category_id == category_id)
        return (await db.execute(query)).scalars().all()

    @classmethod
    async def get_products_from_shop(cls, shop_id):
        query = select(cls).filter(cls.shop_id == shop_id)
        return (await db.execute(query)).scalars().all()


class ProductTip(BaseModel):
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('shop_products.id', ondelete='CASCADE'))
    price: Mapped[int] = mapped_column(BigInteger)
    volume: Mapped[int]
    unit: Mapped[str] = mapped_column(String, nullable=False)

    @classmethod
    async def get_product_tips(cls, id_):
        query = select(cls).filter(cls.product_id == id_)
        return (await db.execute(query)).scalars().all()
