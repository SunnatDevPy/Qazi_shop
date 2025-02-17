from fastapi import APIRouter, Form, HTTPException
from fastapi import Response
from starlette import status

from models import BotUser, Cart, ProductTip, ShopProduct, Shop
from utils.details import detail_cart, get_carts_

cart_router = APIRouter(prefix='/carts', tags=['Cart'])


@cart_router.get(path='', name="Carts")
async def list_category_shop():
    carts = await Cart.all()
    return {"carts": carts}


@cart_router.get(path='/detail', name="Get Cart")
async def list_category_shop(cart_id: int):
    cart = await Cart.get(cart_id)
    if cart:
        return {'cart': cart}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@cart_router.get(path='/from-user', name="Get Cart")
async def list_category_shop(bot_user_id: int):
    carts = await Cart.get_from_bot_user(bot_user_id)
    return {'carts': carts}


@cart_router.get(path='/from-user-shop', name="Get Cart in Shop")
async def list_category_shop(user_id: int, shop_id: int):
    carts = await detail_cart(shop_id, user_id)
    return {'carts': carts}


@cart_router.get(path='/by_user', name="Get Cart in Shop")
async def list_category_shop(user_id: int):
    return await get_carts_(user_id)


@cart_router.post(path='', name="Create Cart from User")
async def list_category_shop(client_id: int,
                             product_id: int = Form(),
                             tip_id: int = Form(),
                             shop_id: int = Form(),
                             count: int = Form()):
    user = await BotUser.get(client_id)
    cart = await Cart.get_cart_from_product(client_id, product_id)
    tip = await ProductTip.get(tip_id)
    product: ShopProduct = await ShopProduct.get(product_id)
    shop: Shop = await Shop.get(shop_id)
    if user:
        if shop:
            if tip:
                if product_id:
                    if cart and cart.tip_id == tip_id:
                        await Cart.update(cart.id, count=count + cart.count, total=cart.total + (count * tip.price))
                    else:
                        cart = await Cart.create(bot_user_id=user.id, product_id=product_id, count=count,
                                                 shop_id=shop_id,
                                                 volume=tip.volume, tip_id=tip_id, unit=tip.unit, price=tip.price,
                                                 total=tip.price * count, product_name_uz=product.name_uz,
                                                 product_name_ru=product.name_ru)
                    return {"ok": True, "cart": cart}
                else:
                    return Response("Product topilmadi", status.HTTP_404_NOT_FOUND)
            else:
                return Response("Tip topilmadi", status.HTTP_404_NOT_FOUND)
        else:
            return Response("Shop topilmadi", status.HTTP_404_NOT_FOUND)
    else:
        return Response("User topilmadi", status.HTTP_404_NOT_FOUND)


@cart_router.delete("/delete", name="Delete Product in cart")
async def user_delete(cart_id: int):
    cart = await Cart.get(cart_id)
    if cart:
        await Cart.delete(cart.id)
        return {"ok": True}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@cart_router.patch(path='', name="Update Cart")
async def list_category_shop(cart_id: int, count: int, minus=None, plus=None):
    cart = await Cart.get(cart_id)
    if cart:
        total = cart.total
        if minus:
            total = (cart.count - count) * cart.price
        elif plus:
            total = count * cart.price
        await Cart.update(cart.id, count=count, total=total)
        return {"ok": True}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)
