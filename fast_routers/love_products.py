from typing import Optional, Annotated, List

from fastapi import APIRouter, File, UploadFile, Form
from fastapi import Response
from pydantic import BaseModel
from sqlalchemy.exc import DBAPIError
from starlette import status

from models import ShopProduct, ShopCategory, AdminPanelUser, Shop, ProductTip, BotUser
from models.products_model import LoveProducts
from utils import FavouritesSchema
from utils.details import get_products_utils, update_products

favourites_router = APIRouter(prefix='/favourites-products', tags=['Favourites'])


@favourites_router.get(path='', name="Get All Favourites")
async def list_category_shop() -> list[FavouritesSchema]:
    return await LoveProducts.all()


@favourites_router.get(path='/detail', name="Get favourites")
async def list_category_shop(favourites_id: int) -> FavouritesSchema:
    product = await LoveProducts.get(favourites_id)
    return product


@favourites_router.get(path='/from-shop', name="Get from Shop Favourites")
async def list_category_shop(shop_id: int) -> list[FavouritesSchema]:
    products = await LoveProducts.get_from_shop(shop_id)
    return products


@favourites_router.get(path='/from-user', name="Get from User and Shop Favourites")
async def list_category_shop(shop_id: int, bot_user_id: int) -> list[FavouritesSchema]:
    products = await LoveProducts.get_cart_from_shop(bot_user_id, shop_id)
    return products


@favourites_router.post(path='', name="Create Product from Favourites")
async def list_category_shop(product_id: int, shop_id: int, bot_user_id: int):
    user: BotUser = await BotUser.get(bot_user_id)
    product: ShopProduct = await ShopProduct.get_shop_product(product_id, shop_id)
    shop = await Shop.get(shop_id)
    if user and shop:
        if product:
            if product.is_active:
                try:
                    products = await LoveProducts.create(shop_id=shop_id, bot_user_id=bot_user_id,
                                                         product_id=product_id,
                                                         is_active=product.is_active)
                    return {"ok": True, "product": products}
                except DBAPIError as e:
                    return Response("Yaratishda xatolik", status.HTTP_404_NOT_FOUND)
            else:
                return Response("Yaratilmadi mahsulot activ emas", status.HTTP_404_NOT_FOUND)

        else:
            return Response("Product topilmadi Shopga tegishli emas", status.HTTP_404_NOT_FOUND)
    else:
        return Response("User yoki shop topilmadi", status.HTTP_404_NOT_FOUND)


@favourites_router.delete(path='', name="Delete Shop Favourites")
async def list_category_shop(favourites_id: int):
    product = await LoveProducts.get(favourites_id)
    if product:
        await LoveProducts.delete(favourites_id)
        return {'ok': True}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)
