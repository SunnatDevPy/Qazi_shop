from typing import Optional

from fastapi import APIRouter, File, UploadFile, Form
from fastapi import Response
from pydantic import BaseModel
from starlette import status

from models import AdminPanelUser, Shop, WorkTimes

shop_router = APIRouter(prefix='/shop', tags=['Shop'])


class ListShopsModel(BaseModel):
    id: Optional[int]
    owner_id: Optional[int]
    name: Optional[str]
    work_status: Optional[str]
    lat: Optional[float]
    long: Optional[float]
    district_uz: Optional[str] = None
    district_ru: Optional[str] = None
    address_uz: Optional[str] = None
    address_ru: Optional[str] = None
    order_group_id: Optional[int] = None
    cart_number: Optional[str] = None
    photo: Optional[str] = None


class UpdateShopsModel(BaseModel):
    owner_id: Optional[int] = None
    name: Optional[str]
    work_status: Optional[str]
    district_uz: Optional[str] = None
    district_ru: Optional[str] = None
    address_uz: Optional[str] = None
    address_ru: Optional[str] = None
    lat: Optional[float]
    long: Optional[float]
    order_group_id: Optional[int] = None
    cart_number: Optional[str] = None
    photo: Optional[str] = None


class CreateShopsModel(BaseModel):
    owner_id: Optional[int] = None
    name: Optional[str] = None
    work_status: Optional[str]
    district_uz: Optional[str] = None
    district_ru: Optional[str] = None
    address_uz: Optional[str] = None
    address_ru: Optional[str] = None
    lat: Optional[float] = None
    long: Optional[float] = None
    order_group_id: Optional[int] = None
    cart_number: Optional[str] = None
    photo: Optional[str] = None


@shop_router.get(path='', name="Shops")
async def list_category_shop():
    shops = await Shop.all()
    return {"shops": shops, "work": await WorkTimes.all()}


@shop_router.get(path='/detail', name="Get Shop")
async def list_category_shop(shop_id: int):
    shop = await Shop.get(shop_id)
    if shop:
        return {'shop': shop}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@shop_router.post(path='', name="Create Shop")
async def list_category_shop(owner_id: int,
                             name_uz: str = Form(default=None),
                             name_ru: str = Form(None),
                             district_uz: str = Form(None),
                             district_ru: str = Form(None),
                             address_uz: str = Form(None),
                             address_ru: str = Form(None),
                             lat: float = Form(None),
                             long: float = Form(None),
                             order_group_id: int = Form(None),
                             cart_number: int = Form(None),
                             photo: UploadFile = File(None)
                             ):
    user: AdminPanelUser = await AdminPanelUser.get(owner_id)
    if user:
        if user.status in ['moderator', "admin", "superuser"]:
            shop = await Shop.create(owner_id=owner_id, name_uz=name_uz,
                                     name_ru=name_ru,
                                     district_uz=district_uz,
                                     address_uz=address_uz,
                                     address_ru=address_ru,
                                     district_ru=district_ru, lat=lat, long=long,
                                     photo=photo, work_status='CLOSE',
                                     order_group_id=order_group_id, cart_number=cart_number)
            return {"ok": True, "shop_id": shop.id}
        else:
            return Response("Bu userda xuquq yo'q", status.HTTP_404_NOT_FOUND)
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


# Update Shop
@shop_router.patch(path='/detail', name="Update Shop")
async def list_category_shop(operator_id: int,
                             shop_id: int,
                             name_uz: str = Form(default=None),
                             name_ru: str = Form(None),
                             work_status: str = Form(None),
                             district_uz: str = Form(None),
                             district_ru: str = Form(None),
                             address_uz: str = Form(None),
                             address_ru: str = Form(None),
                             lat: float = Form(None),
                             long: float = Form(None),
                             order_group_id: int = Form(None),
                             cart_number: int = Form(None),
                             photo: UploadFile = File(None)
                             ):
    user: AdminPanelUser = await AdminPanelUser.get(operator_id)
    shop: Shop = await Shop.get(shop_id)
    if user and shop:
        if photo:
            if not photo.content_type.startswith("image/"):
                return Response("fayl rasim bo'lishi kerak", status.HTTP_404_NOT_FOUND)
        update_data = {k: v for k, v in {
            "name_uz": name_uz,
            "name_ru": name_ru,
            "district_uz": district_uz,
            "district_ru": district_ru,
            "address_uz": address_uz,
            "address_ru": address_ru,
            "lat": lat,
            "long": long,
            "order_group_id": order_group_id,
            "work_status": work_status,
            "cart_number": cart_number}.items() if v is not None}
        if user.status in ['moderator', "admin", "superuser"] or user.id == shop.owner_id:
            await Shop.update(shop_id, **update_data)
            return {"ok": True, "shop": shop}
        else:
            return Response("Bu userda xuquq yo'q", status.HTTP_404_NOT_FOUND)
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@shop_router.delete(path='', name="Delete Shop")
async def list_category_shop(operator_id: int, shop_id: int):
    user: AdminPanelUser = await AdminPanelUser.get(operator_id)
    shop: Shop = await Shop.get(shop_id)
    if user and shop:
        if user.status in ["moderator", "admin", "superuser"]:
            await Shop.delete(shop)
            return Response("Item Not Found", status.HTTP_404_NOT_FOUND)
        else:
            return Response("AdminPanelUserda xuquq yo'q", status.HTTP_404_NOT_FOUND)
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)
