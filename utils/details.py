from models import Cart, ShopProduct, ShopCategory, Shop, \
    BotUser, OrderItem, Order, ProductTip


async def sum_price_carts(carts: list['Cart']):
    sum_ = 0
    for i in carts:
        sum_ += i.total
    return sum_


async def detail_cart(shop_id, user_id):
    user = await BotUser.get(user_id)
    carts: list['Cart'] = await Cart.get_cart_from_shop(user.id, shop_id)
    cart_ = []
    for i in carts:
        product: 'ShopProduct' = await ShopProduct.get(i.product_id)
        cart_.append({
            'id': i.id,
            "bot_user_id": i.bot_user_id,
            "shop_id": i.shop_id,
            "product_id": i.product_id,
            "unit": i.unit,
            "volume": i.volume,
            "count": i.count,
            "price": i.price,
            "total": i.total
        })
    return cart_


async def get_products_utils(shop_id):
    categories: list['ShopCategory'] = await ShopCategory.get_shop_categories(shop_id)
    category = []
    for i in categories:
        products: list['ShopProduct'] = await ShopProduct.get_products_category(i.id)
        category.append({'category': i, "products": products})
    return category


async def get_carts_(user_id):
    shops = await Shop.all()
    list_ = []
    for i in shops:
        cart_from_shop = await Cart.get_cart_from_shop(user_id, i.id)
        list_.append({"shop": i, "carts": cart_from_shop})
    return list_


async def detail_orders(orders: list['Order']):
    detail_ = []
    for i in orders:
        order_items: list['OrderItem'] = await OrderItem.get_order_items(i.id)
        items = []
        for j in order_items:
            product = await ShopProduct.get(j.product_id)
            items.append({'name': product.name, "price": j.price, "count": j.count,
                          "total": j.total})
        detail_.append({"order": i, "order_items": items})
    return detail_


async def detail_orders_types(user_id, shop_id=None):
    types = ["YANGI"
             "Yig'ilmoqda",
             "YETKAZILMOQDA",
             "YETKAZILDI",
             "BEKOR QILINDI"]
    if shop_id:
        pass
    else:
        pass
    detail_ = []
    for i in types:
        if shop_id:
            detail_.append({i: await Order.get_from_bot_user_in_type_and_shop(user_id, i, shop_id)})
        else:
            detail_.append({i: await Order.get_from_bot_user_in_type(user_id, i)})
    return detail_


async def update_products(products):
    list_ = []
    for i in products:
        shop = await Shop.get(i.shop_id)
        i.shop = shop
        list_.append(i)
    return list_


# Оптимизация корзины

async def detail_order(order):
    order_items: list['OrderItem'] = await OrderItem.get_order_items(order.id)
    text = ''
    count = 1
    for i in order_items:
        product = await ShopProduct.get(i.product_id)
        text += f"{count}) {product.name} {i.price} x {i.count} = {i.total}\n"
    return f"""
<b>Buyurtma soni</b>: {order.id}
<b>Ism-Familiya</b>: {order.first_last_name}
<b>Manzil</b>: {order.address}
<b>Tel</b>: {order.contact}
<b>To'lov turi</b>: {order.payment}

<b>Mahsulotlar</b>
{text}

<b>Yo'l kira narxi</b>: {order.driver_price}
<b>Umumiy summa</b>: {order.total_sum}
    """


async def all_data():
    shops = await Shop.all()
    shop = []
    for i in shops:
        product = []
        categories: list[ShopCategory] = await ShopCategory.get_shop_categories(i.id)
        for j in categories:
            j.products = await ShopProduct.get_products_category(j.id)
            product.append(j)
        i.category = product
        shop.append(i)
    return shop


async def tips_model(tips: list):
    for i in tips:
        pass