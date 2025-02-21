from typing import Optional, Annotated

from fastapi import APIRouter, Form
from fastapi import Response
from geopy.distance import geodesic
from pydantic import BaseModel
from starlette import status

from dispatcher import bot
from models import BotUser, Shop, Cart, Order, OrderItem
from utils.details import detail_order, sum_price_carts

order_router = APIRouter(prefix='/order', tags=['Orders'])


class OrderItemsModel(BaseModel):
    id: int
    product_id: int
    order_id: int
    count: int
    volume: int
    unit: str
    price: int
    total: int


class OrderModel(BaseModel):
    id: int
    payment: str
    status: str
    bot_user_id: int
    address: str
    shop_id: int
    first_last_name: str
    contact: str
    driver_price: int
    total_sum: int
    lat: float
    long: float
    order_items: Optional[list[OrderItemsModel]] = None


@order_router.get(path='', name="Orders")
async def list_category_shop() -> list[OrderModel]:
    orders = await Order.all()
    return orders


@order_router.get(path='/detail', name="Get Orders")
async def list_category_shop(cart_id: int) -> OrderModel:
    order = await Order.get(cart_id)
    return order


@order_router.get(path='/from-user', name="Get Orders from User")
async def list_category_shop(user_id: int, shop_id: int) -> list[OrderModel]:
    # orders = await detail_orders_types(user_id)
    orders = await Order.get_cart_from_shop(user_id, shop_id)
    return orders


@order_router.get(path='/from-status', name="Get Order from Status in User")
async def list_category_shop(user_id: int, status_order: str):
    if status_order not in ['yangi', 'NEW', "IS_GOING", "yig'ilmoqda",
                            "IN_PROGRESS", "yetkazilmoqda",
                            "DELIVERED", "yetkazildi",
                            "CANCELLED", "bekor qilindi"]:
        return Response("Buyurtmaga notog'ri status berilgan", status.HTTP_404_NOT_FOUND)
    orders = await Order.get_from_bot_user_in_type(user_id, type)
    if orders:
        return {'orders': orders}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


# @order_router.get(path='/from-shop', name="Get Cart from User in Shop")
# async def list_category_shop(user_id: int, shop_id: int):
#     orders = await detail_orders_types(user_id, shop_id)
#     if orders:
#         return {'orders': orders}
#     else:
#         return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


class CreateOrder(BaseModel):
    payment: str
    long: float
    lat: float
    contact: str
    address: str
    first_last_name: str


@order_router.post(path='', name="Create Order from User")
async def list_category_shop(client_id: int, shop_id: int, items: Annotated[CreateOrder, Form()]):
    user = await BotUser.get(client_id)
    shop = await Shop.get(shop_id)
    if items.payment not in ['CASH', "TERMINAL", "karta", 'naqt']:
        return Response("Payment type notog'ri yuborildi", status.HTTP_404_NOT_FOUND)

    if user:
        if shop:
            carts: list['Cart'] = await Cart.get_cart_from_shop(client_id, shop_id)
            if carts:
                try:
                    distance_km = geodesic((shop.lat, shop.long), (items.lat, items.long)).kilometers
                except:
                    distance_km = 0
                sum_order = await sum_price_carts(carts)

                order = await Order.create(**items.dict(), total_sum=sum_order, driver_price=distance_km,
                                           shop_id=shop_id, bot_user_id=client_id,  status="NEW")
                order_items_ = []
                for cart in carts:
                    s = await OrderItem.create(product_id=cart.product_id, order_id=order.id, count=cart.count,
                                               volume=cart.tip.volume, unit=cart.tip.unit, price=cart.tip.price,
                                               total=cart.total)
                    order_items_.append(s)
                    await Cart.delete(cart.id)
                message = None
                try:
                    location = await bot.send_location(shop.order_group_id, latitude=order.lat, longitude=order.long)
                    await bot.send_message(shop.order_group_id, await detail_order(order), parse_mode="HTML",
                                           reply_to_message_id=location.message_id)
                except:
                    message = 'Buyurtma yaratildi lekin guruxga yuborishda hatolik'
                return {"ok": True,
                        "message": "Buyurtma qabul qilindi va guruxga yuborildi" if message == None else message,
                        "order": order,
                        "order_items": order_items_}
            else:
                return Response("Savat topilmadi", status.HTTP_404_NOT_FOUND)
        else:
            return Response("Shop topilmadi", status.HTTP_404_NOT_FOUND)
    else:
        return Response("User topilmadi", status.HTTP_404_NOT_FOUND)


class UpdateOrder(BaseModel):
    order_status: Optional[str] = None


@order_router.patch(path='', name="Update Order")
async def list_category_shop(order_id: int, items: Annotated[UpdateOrder, Form()]):
    if items.status not in ['yangi', 'NEW', "IS_GOING", "yig'ilmoqda",
                            "IN_PROGRESS", "yetkazilmoqda",
                            "DELIVERED", "yetkazildi",
                            "CANCELLED", "bekor qilindi"]:
        return Response("Buyurtmaga notog'ri status berilgan", status.HTTP_404_NOT_FOUND)
    order = await Order.get(order_id)
    if order:
        update_data = {k: v for k, v in items.dict().items() if v is not None}
        await Order.update(order_id, **update_data)
        return {"ok": True, "order": order}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@order_router.patch(path='/canceled', name="Canceled Order")
async def list_category_shop(order_id: int):
    order = await Order.get(order_id)
    if order:
        await Order.update(order.id, status="CANCELLED")
        return {"ok": True, "order": order}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)
