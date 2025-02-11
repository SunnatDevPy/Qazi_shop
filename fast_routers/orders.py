from typing import Optional, Annotated

from fastapi import APIRouter, Form
from fastapi import Response
from geopy.distance import geodesic
from pydantic import BaseModel
from starlette import status

from dispatcher import bot
from fast_routers import geolocator
from models import BotUser, Shop, Cart, Order, OrderItem, MyAddress
from utils.details import detail_order, sum_price_carts, detail_orders_types

order_router = APIRouter(prefix='/order', tags=['Orders'])


@order_router.get(path='', name="Orders")
async def list_category_shop():
    orders = await Order.all()
    return {"orders": orders}


@order_router.get(path='/detail', name="Get Orders")
async def list_category_shop(cart_id: int):
    order = await Order.get(cart_id)
    if order:
        return {'order': order}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@order_router.get(path='/from-user', name="Get Orders from User")
async def list_category_shop(user_id: int):
    orders = await detail_orders_types(user_id)
    if orders:
        return {'orders': orders}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@order_router.get(path='/from-type', name="Get Order from Type in User")
async def list_category_shop(user_id: int, type: str):
    orders = await Order.get_from_bot_user_in_type(user_id, type)
    if orders:
        return {'orders': orders}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@order_router.get(path='/from-shop', name="Get Cart from User in Shop")
async def list_category_shop(user_id: int, shop_id: int):
    orders = await detail_orders_types(user_id, shop_id)
    if orders:
        return {'orders': orders}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@order_router.post(path='', name="Create Order from User")
async def list_category_shop(client_id: int,
                             shop_id: int,
                             payment_type: str,
                             phone: str,
                             long: int,
                             lat: int):
    user = await BotUser.get(client_id)
    shop = await Shop.get(shop_id)
    if user and shop:
        carts: list['Cart'] = await Cart.get_cart_from_shop(client_id, shop_id)
        distance_km = geodesic((shop.lat, shop.long), (user.lat, user.long)).kilometers
        sum_order = sum_price_carts(carts)
        location = geolocator.reverse(f"{lat}, {long}")
        address = location.raw['address']
        if address:
            await MyAddress.create(bot_user_id=client_id, lat=lat, long=long,
                                   name=f"{address['county']}, {address['neighbourhood']}, {address['road']}")
        order = await Order.create(user_id=client_id, payment=payment_type, status="NEW", shop_id=shop_id,
                                   total_sum=sum_order,
                                   address=address, last_first_name=f"{user.first_name} {user.last_name}",
                                   contact=phone, long=long, lat=lat,
                                   driver_price=0 if sum_order[0] > 1500000 else 50000 * distance_km)
        order_items = []
        for i in carts:
            s = await OrderItem.create(product_id=i.product_id, order_id=order.id, count=i.count,
                                       volume=i.volume, unit=i.unit, price=i.price, total=i.total)
            order_items.append(s)
            await Cart.delete(i.id)
        try:
            await bot.send_message(shop.order_group_id, await detail_order(order), parse_mode="HTML")
        except:
            await bot.send_message(user.id, await detail_order(order), parse_mode="HTML")
        return {"ok": True, "message": "Buyurtma qabul qilindi va guruxga yuborildi ", "order": order,
                "order_items": order_items}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


class UpdateOrder(BaseModel):
    status: Optional[str] = None


@order_router.post(path='', name="Update Order")
async def list_category_shop(order_id: int, items: Annotated[UpdateOrder, Form()]):
    order = await Order.get(order_id)
    if order:
        update_data = {k: v for k, v in items.dict().items() if v is not None}
        await Order.update(order_id, **update_data)
        return {"ok": True, "order": order}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@order_router.post(path='/canceled', name="Canceled Order")
async def list_category_shop(user_id: int, order_id: int):
    order = await Order.get(order_id)
    if order:
        await Order.update(order.id, status="CANCELLED")
        return {"ok": True, "order": order}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)
