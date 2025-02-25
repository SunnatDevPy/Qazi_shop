from typing import Optional, List

from fastapi import APIRouter, File, UploadFile, Form
from fastapi import Response
from pydantic import BaseModel
from sqlalchemy.exc import DBAPIError
from starlette import status

from models import AdminPanelUser, Shop
from utils.details import all_data

shop_router = APIRouter(prefix='/shop', tags=['Shop'])


class WorkModel(BaseModel):
    id: int
    shop_id: int
    open_time: str
    close_time: str
    weeks: list


class ListShopsModel(BaseModel):
    id: Optional[int]
    owner_id: Optional[int]
    name_uz: Optional[str]
    name_ru: Optional[str]
    work_status: Optional[str]
    lat: Optional[float]
    long: Optional[float]
    district_uz: Optional[str] = None
    district_ru: Optional[str] = None
    address_uz: Optional[str] = None
    address_ru: Optional[str] = None
    order_group_id: Optional[int] = None
    cart_number: Optional[int] = None
    photo: Optional[str] = None
    is_active: Optional[bool] = None
    work: Optional[List[WorkModel]] = None


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
async def list_category_shop() -> list[ListShopsModel]:
    return await Shop.all()


@shop_router.get(path='/detail', name="Get Shop")
async def list_category_shop(shop_id: int):
    shop = await Shop.get(shop_id)
    if shop:
        return {'shop': shop}
    else:
        return Response("Item Not Found", status.HTTP_404_NOT_FOUND)


@shop_router.get(path='/all', name="Get Shop")
async def list_category_shop():
    return await all_data()


@shop_router.post(path='', name="Create Shop")
async def list_category_shop(owner_id: int,
                             name_uz: str = Form(),
                             name_ru: str = Form(),
                             district_uz: str = Form(),
                             district_ru: str = Form(),
                             address_uz: str = Form(),
                             address_ru: str = Form(),
                             lat: float = Form(),
                             long: float = Form(),
                             is_active: bool = Form(default=True),
                             order_group_id: int = Form(),
                             cart_number: int = Form(),
                             photo: UploadFile = File()
                             ):
    user: AdminPanelUser = await AdminPanelUser.get(owner_id)
    if user:
        if user.status in ['moderator', "admin", "superuser"]:
            try:
                shop = await Shop.create(owner_id=owner_id, name_uz=name_uz,
                                         name_ru=name_ru,
                                         district_uz=district_uz,
                                         address_uz=address_uz,
                                         address_ru=address_ru,
                                         district_ru=district_ru, lat=lat, long=long,
                                         photo=photo, work_status='CLOSE', is_active=is_active,
                                         order_group_id=order_group_id, cart_number=cart_number)
            except DBAPIError as e:
                print(e)
                return Response("Yaratishda hatolik", status.HTTP_404_NOT_FOUND)

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
                             is_active: bool = Form(None),
                             photo: UploadFile = File(None)
                             ):
    user: AdminPanelUser = await AdminPanelUser.get(operator_id)
    shop: Shop = await Shop.get(shop_id)
    if user and shop:
        if photo:
            if not photo.content_type.startswith("image/"):
                return Response("fayl rasim bo'lishi kerak", status.HTTP_404_NOT_FOUND)
        if work_status not in ['OPEN', 'ochiq', 'yopiq', "CLOSE"]:
            return Response("Work timeda hatolik: keyga (ochiq yoki OPEN, yopiq yoki CLOSE) yuboring",
                            status.HTTP_404_NOT_FOUND)

        update_data = {k: v for k, v in {
            "name_uz": name_uz,
            "name_ru": name_ru,
            "district_uz": district_uz,
            "district_ru": district_ru,
            "address_uz": address_uz,
            "address_ru": address_ru,
            "lat": lat,
            "long": long,
            "is_active": is_active,
            "order_group_id": order_group_id,
            "work_status": work_status,
            "cart_number": cart_number}.items() if v is not None}
        if user.status in ['moderator', "admin", "superuser"] or user.id == shop.owner_id:
            if update_data:
                try:
                    await Shop.update(shop_id, **update_data)
                    return {"ok": True, "shop": shop}
                except DBAPIError as e:
                    print(e)
                    return Response(f"O'zgarishda hatolik: {e}", status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response("O'zgarishda malumot yoq", status.HTTP_500_INTERNAL_SERVER_ERROR)
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
