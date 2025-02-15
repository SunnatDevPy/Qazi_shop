from typing import Optional, Annotated, List

from fastapi import APIRouter, File, UploadFile, Form
from fastapi import Response
from pydantic import BaseModel
from starlette import status

from models import ShopProduct, ShopCategory, AdminPanelUser, Shop, ProductTip
from utils.details import get_products_utils, update_products

shop_product_router = APIRouter(prefix='/shop-products', tags=['Shop Products'])


# @product_router.post("/")
# async def read_item(request: Request):
#     data = await request.form()
#     await Product.create(**data)
#     return RedirectResponse('/products')


# @product_router.get("/", name='product_list')
# async def get_all_products(request: Request, category: int = None, search: str = None):
#     if category:
#         subquery = select(Category.id).where(or_(Category.parent_id == category, Category.id == category))
#         products = await Product.filter(Product.category_id.in_(subquery))
#     else:
#         products = await Product.all()
#
#     # products = await Product.filter(Product.category_id.in_([1, 2]), columns=(Product, (Product.price * sum_price).label('price_sum')))
#
#     # if search:
#     #     products = await products.filter(or_(Product.name.ilike(f'%{search}%'), Product.description.ilike(f'%{search}%')))
#
#     categories = await Category.filter(Category.parent_id == None, relationship=Category.subcategories)
#
#     context = {
#         'products': products,
#         'categories': categories
#     }
#     return templates.TemplateResponse(request, 'apps/products/product-list.html', context)

class ProductTipSchema(BaseModel):
    price: int
    volume: int
    unit: str
    product_id: int


class ProductList(BaseModel):
    id: int
    name_uz: str
    name_ru: str
    description_uz: str
    description_ru: str
    owner_id: int
    category_id: int
    photo: str
    shop_id: int
    is_active: bool
    price: int
    volume: int
    unit: int
    tips: Optional[List[ProductTipSchema]] = None  # Prevent recursion

    class Config:
        from_attributes = True
        exclude_unset = True


@shop_product_router.get(path='', name="Get All Products")
async def list_category_shop() -> list[ProductList]:
    return await ShopProduct.all()


@shop_product_router.get(path='/detail', name="Get Product")
async def list_category_shop(product_id: int):
    product = await ShopProduct.get(product_id)
    product.tips = await ProductTip.get_product_tips(product_id)
    return {"product": product}


@shop_product_router.get(path='/from-shop', name="Get from Shop Products")
async def list_category_shop(shop_id: int):
    products = await get_products_utils(shop_id)
    if products:
        return products
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@shop_product_router.post(path='', name="Create Product from Category")
async def list_category_shop(operator_id: int,
                             name_uz: str = Form(),
                             name_ru: str = Form(),
                             description_uz: str = Form(),
                             description_ru: str = Form(),
                             category_id: int = Form(default=None),
                             shop_id: int = Form(),
                             price: int = Form(None),
                             volume: int = Form(None),
                             unit: str = Form(None),
                             photo: UploadFile = File(default=None), ):
    user: AdminPanelUser = await AdminPanelUser.get(operator_id)
    category = await ShopCategory.get_from_shop(shop_id, category_id)
    shop = await Shop.get(shop_id)
    if user and shop:
        if category:
            if user.status in ['moderator', "admin", "superuser"] or user.id == shop.owner_id:
                product = await ShopProduct.create(
                    name_uz=name_uz,
                    name_ru=name_ru,
                    owner_id=operator_id,
                    category_id=category_id,
                    description_uz=description_uz,
                    description_ru=description_ru,
                    photo=photo,
                    shop_id=shop_id,
                    price=price,
                    volume=volume,
                    unit=unit,
                    is_active=True
                )
                return {"ok": True, "id": product.id}

            else:
                return Response("Bu userda xuquq yo'q", status.HTTP_404_NOT_FOUND)
        else:
            return Response("Category id shop id ga tegishli emas", status.HTTP_404_NOT_FOUND)
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@shop_product_router.get(path='/search', name="search")
async def list_category_shop(search: Optional[str] = None, category_id: Optional[int] = None):
    category = await ShopCategory.get(category_id)
    if category:
        products = await ShopProduct.search_shops(search, category_id)
    else:
        products = await ShopProduct.search_shops(search)
    return {"products": await update_products(products)}


# Update Shop
@shop_product_router.patch(path='/detail', name="Update Shop Product")
async def list_category_shop(operator_id: int,
                             shop_product_id: int = Form(),
                             name_uz: str = Form(),
                             name_ru: str = Form(),
                             description_uz: str = Form(),
                             description_ru: str = Form(),
                             category_id: int = Form(default=None),
                             is_active: bool = Form(None),
                             price: int = Form(None),
                             volume: int = Form(None),
                             unit: str = Form(None),
                             photo: UploadFile = File(default=None),
                             ):
    user: AdminPanelUser = await AdminPanelUser.get(operator_id)
    product = await ShopProduct.get(shop_product_id)
    if photo:
        if not photo.content_type.startswith("image/"):
            return Response("fayl rasim bo'lishi kerak", status.HTTP_404_NOT_FOUND)
    if user and product:
        update_data = {k: v for k, v in
                       {"category_id": category_id, "name_uz": name_uz, "photo": photo,
                        "name_ru": name_ru, "description_uz": description_uz, "description_ru": description_ru,
                        "is_active": is_active, "price": price,
                        "volume": volume,
                        "unit": unit, }.items()
                       if
                       v is not None}

        if user.status in ['moderator', "admin", "superuser"] or user.id == product.owner_id:
            await ShopProduct.update(shop_product_id, **update_data)
            return {"ok": True}
        else:
            return Response("Bu userda xuquq yo'q", status.HTTP_404_NOT_FOUND)
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@shop_product_router.delete(path='', name="Delete Shop Products")
async def list_category_shop(operator_id: int, shop_product_id: int):
    user: AdminPanelUser = await AdminPanelUser.get(operator_id)
    product = await ShopProduct.get(shop_product_id)
    if user and product:
        if user.status in ['moderator', "admin", "superuser"] or user.id == product.owner_id:
            await ShopProduct.delete(shop_product_id)
            return Response("Item Not Found", status.HTTP_404_NOT_FOUND)
        else:
            return Response("Userda xuquq yo'q", status.HTTP_404_NOT_FOUND)
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


# ================= Product Tips =============================


@shop_product_router.get(path='/tips', name="Get All Product tips")
async def list_category_shop():
    tips = await ProductTip.all()
    return {"tips": tips}


@shop_product_router.get(path='/tips/detail', name="Get product tip")
async def list_category_shop(product_tip_id: int):
    tip = await ProductTip.get(product_tip_id)
    return {"tip": tip}


@shop_product_router.get(path='/tips/from-product', name="Get from Products")
async def list_category_shop(product_tip_id: int):
    tips = await ProductTip.get_product_tips(product_tip_id)
    if tips:
        return tips
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@shop_product_router.post(path='/tips', name="Create Product Tips")
async def list_category_shop(operator_id: int,
                             product_id: int = Form(),
                             price: int = Form(),
                             volume: int = Form(),
                             unit: str = Form()):
    user: AdminPanelUser = await AdminPanelUser.get(operator_id)
    product = await ShopCategory.get(product_id)
    if user:
        if product:
            if user.status in ['moderator', "admin", "superuser"]:
                tip = await ProductTip.create(
                    product_id=product_id,
                    price=price,
                    volume=volume,
                    unit=unit,

                )
                return {"ok": True, "tip": tip}
            else:
                return Response("Bu userda xuquq yo'q", status.HTTP_404_NOT_FOUND)
        else:
            return Response("Category id shop id ga tegishli emas", status.HTTP_404_NOT_FOUND)
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


class UpdateTips(BaseModel):
    product_id: Optional[int] = None,
    price: Optional[int] = None,
    volume: Optional[int] = None,
    unit: Optional[str] = None


# Update Shop
@shop_product_router.patch(path='/tips/detail', name="Update Product Tips")
async def list_category_shop(operator_id: int, product_tip_id: int, items: Annotated[UpdateTips, Form()]):
    user: AdminPanelUser = await AdminPanelUser.get(operator_id)
    tip = await ProductTip.get(product_tip_id)
    if user and tip:
        update_data = {k: v for k, v in items.dict().items() if v is not None}
        if user.status in ['moderator', "admin", "superuser"]:
            await ProductTip.update(product_tip_id, **update_data)
            return {"ok": True}
        else:
            return Response("Bu userda xuquq yo'q", status.HTTP_404_NOT_FOUND)
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@shop_product_router.delete(path='/tips', name="Delete Product tip")
async def list_category_shop(operator_id: int, product_tip_id: int):
    user: AdminPanelUser = await AdminPanelUser.get(operator_id)
    tip = await ProductTip.get(product_tip_id)
    if user and tip:
        if user.status in ['moderator', "admin", "superuser"]:
            await ProductTip.delete(tip)
            return Response("Item Not Found", status.HTTP_404_NOT_FOUND)
        else:
            return Response("Userda xuquq yo'q", status.HTTP_404_NOT_FOUND)
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)
